import copy
import json
import logging
import os
import pprint
import tempfile
import time
from typing import Any, List, Optional

import requests
import strangeworks as sw
import yaml
from strangeworks.core.client.backends import Backend
from strangeworks.core.client.jobs import Job
from strangeworks.core.client.resource import Resource
from strangeworks.core.errors.error import StrangeworksError
from strangeworks_core.types.job import Status
from strangeworks_optimization_models.parameter_models import (
    AquilaParameterModel,
    DwaveLeapParameterModel,
    DwaveSamplerParameterModel,
    DwaveSWHybridParameterModel,
    FujitsuParameterModel,
    GurobiParameterModel,
    HitachiParameterModel,
    JijParameterModel,
    LightSolverParameterModel,
    NEC2ParameterModel,
    NEC3ParameterModel,
    NECParameterModel,
    QAOAParameterModel,
    QuantagoniaParameterModel,
    SWHybridParameterModel,
    ToshibaParameterModel,
)
from strangeworks_optimization_models.problem_models import (
    RemoteFile,
    StrangeworksModel,
    StrangeworksModelFactory,
)
from strangeworks_optimization_models.solution_models import (
    StrangeworksSolution,
    StrangeworksSolutionFactory,
)
from strangeworks_optimization_models.solver_models import (
    StrangeworksSolver,
    StrangeworksSolverFactory,
)
from strangeworks_optimization_models.strangeworks_models import (
    StrangeworksOptimizationJob,
    StrangeworksOptimizationModel,
    StrangeworksOptimizationSolution,
    StrangeworksOptimizationSolver,
)


def _get_product_slug(label_name: str) -> str:
    if label_name in ["jij"]:
        return "jijzept"
    elif label_name in ["azure"]:
        return "azure-quantum"
    elif label_name in ["braket"]:
        return "amazon-braket"
    elif label_name in ["sim"]:
        return "simulated-sampler"
    return label_name


class StrangeworksOptimizer:
    """Strangeworks optimization controller."""

    model: StrangeworksModel | None = None
    solver: StrangeworksSolver | None = None
    solution: StrangeworksSolution | None = None
    job: Job | None = None
    tags: List[str] | None = None
    print_deprecated_version_message = True

    def __init__(
        self,
        model: Any | None = None,
        solver: Any | None = None,
        options: (
            AquilaParameterModel
            | DwaveLeapParameterModel
            | DwaveSamplerParameterModel
            | FujitsuParameterModel
            | GurobiParameterModel
            | HitachiParameterModel
            | JijParameterModel
            | NECParameterModel
            | NEC2ParameterModel
            | NEC3ParameterModel
            | QuantagoniaParameterModel
            | ToshibaParameterModel
            | SWHybridParameterModel
            | None
        ) = None,
        solution: Any | None = None,
        resource_slug: str | None = None,
        tags: List[str] | None = None,
    ) -> None:
        """Initialize the StrangeworksOptimizer.

        If a resource slug is provided, confirm it exists and set is as resource for
        its product. If there is no resource associated with the given slug, raise
        error.

        If no resource slug is provided, try retrieving a resource slug for the
        optimization service. If the user does not have a resource configured, raise
        error.

        Parameters
        ----------
        model: Any | None
            The model that will be used by the optimizer.
        solver: Any | None
            The solver to use for optimization.
        options: dict | None
            Options to pass to the optimizer.
        solution: Any | None
            Solution to be used.
        resource_slug: str | None
            Allows user to specify a specific resource to use.
        tags: List[str] | None
            List of user specified tags that will be associated with the job.
        """

        # Print out small warning when not using latest SDK version
        if StrangeworksOptimizer.print_deprecated_version_message:
            try:
                response = requests.get("https://pypi.org/pypi/strangeworks-optimization/json")
                if response.status_code == 200:
                    latest_version = response.json()["info"]["version"]
                    import strangeworks_optimization as so

                    current_version = so.__version__

                    if current_version != latest_version:
                        print(
                            f"Warning: You are using strangeworks-optimization version {current_version} while the latest is {latest_version}"
                        )

                    del so
            except Exception as e:
                print(
                    f"While attempting to check if strangeworks-optimization is latest version, encountered an error: {str(e)}"
                )
            StrangeworksOptimizer.print_deprecated_version_message = False

        if model and not isinstance(model, RemoteFile):
            model = self.upload_model(model)
        self.model = StrangeworksModelFactory.from_model(model) if model else None

        if solver:
            self.solver = StrangeworksSolverFactory.from_solver(solver)
            self._init_solver()

        if tags:
            self.tags = tags
        else:
            self.tags = None

        self.options = options
        self.solution = StrangeworksSolutionFactory.from_solution(solution)

        if resource_slug:
            sw.set_resource_for_product(resource_slug=resource_slug, product_slug="optimization")
        self.resource: Resource = sw.get_resource_for_product("optimization")

    def _init_solver(self):
        if self.solver:
            product_slug = _get_product_slug(self.solver.provider)
            self.sub_rsc = sw.get_resource_for_product(product_slug)

            self.solver.strangeworks_parameters = {
                "sub_product_slug": self.sub_rsc.product.slug,
                "sub_resource_slug": self.sub_rsc.slug,
            }

    def run(self) -> Job | None:
        solver = StrangeworksOptimizationSolver.from_solver(self.solver)
        if not self.check_parameter_model_compatibility(solver.solver.split(".", 1)[0], solver.solver, self.options):
            raise StrangeworksError(f"Parameter option {self.options} is not compatible with {solver.solver}")

        if self.tags:
            for tag in self.tags:
                if len(tag) > 35:
                    raise StrangeworksError("Tag length cannot be greater than 35 characters")

            sw_params = json.loads(solver.strangeworks_parameters)
            sw_params["tags"] = self.tags
            solver.strangeworks_parameters = json.dumps(sw_params)

        if self.options:
            # Transform options class to dict and remove entries that are None
            options = copy.deepcopy(self.options.__dict__)
            for k, v in self.options.__dict__.items():
                if v is None:
                    options.pop(k)
        solver.solver_options = json.dumps(options) if self.options else json.dumps(None)

        strangeworks_optimization_job = StrangeworksOptimizationJob(
            model=StrangeworksOptimizationModel.from_model(self.model),
            solver=solver,
            solution=StrangeworksOptimizationSolution.from_solution(self.solution) if self.solution else None,
        )
        res = sw.execute(self.resource, payload=strangeworks_optimization_job.model_dump(), endpoint="run")

        job_slug = json.loads(res["solution"]["strangeworks_parameters"])["job_slug"]
        self.job = sw.jobs(slug=job_slug)[0]
        return self.job

    def run_batch(self, batch_file: str) -> dict[str, Job]:
        with open(batch_file) as stream:
            yam = yaml.safe_load(stream)

        tagbatch = yam["job_name"]

        # Make sure run names are unique. Becuase we are using the run names as keys for the returned dict
        if len(yam["runs"]) != len(set([job["run"] for job in yam["runs"]])):
            raise ValueError("Run names must be unique")

        sw_jobs = {}
        for job in yam["runs"]:
            tagjob = job["run"]
            problem_params = job["problem_parameters"]

            remote_model = RemoteFile(model_url=problem_params["model_url"], model_type=problem_params["model_type"])

            provider = problem_params["solver"].split(".", 1)[0]

            options = self.get_options(provider, problem_params["solver"], problem_params["solver_options"])

            optimizer = StrangeworksOptimizer(
                model=remote_model,
                solver=problem_params["solver"],
                options=options,
                resource_slug=self.resource.slug,
                tags=[tagbatch, tagjob],
            )

            sw_jobs[tagjob] = optimizer.run()

        return sw_jobs

    def check_parameter_model_compatibility(self, provider: str, solver: str, parameter_model: Any) -> bool:
        if parameter_model:
            if provider == "dwave":
                if "sw_hybrid" in solver:
                    return isinstance(parameter_model, DwaveSWHybridParameterModel)
                elif (
                    solver == "dwave.hybrid_binary_quadratic_model_version2p"
                    or solver == "dwave.hybrid_constrained_quadratic_model_version1p"
                    or solver == "dwave.hybrid_discrete_quadratic_model_version1p"
                    or solver == "dwave.hybrid_nonlinear_program_version1p"
                ):
                    return isinstance(parameter_model, DwaveLeapParameterModel)
                else:
                    return isinstance(parameter_model, DwaveSamplerParameterModel)
            elif provider == "sim":
                if solver == "sim.dimod_simulated_annealing_sampler" or solver == "sim.dimod_random_sampler":
                    return isinstance(parameter_model, DwaveSamplerParameterModel)
                else:
                    # Leaving open for now, for other future types of simulators that require different parameter models  # noqa
                    return False
            elif provider == "gurobi":
                return isinstance(parameter_model, GurobiParameterModel)
            elif provider == "quantagonia":
                return isinstance(parameter_model, QuantagoniaParameterModel)
            elif provider == "hitachi":
                return isinstance(parameter_model, HitachiParameterModel)
            elif provider == "toshiba" or provider == "toshiba-p3-16xl":
                return isinstance(parameter_model, ToshibaParameterModel)
            elif provider == "fujitsu":
                return isinstance(parameter_model, FujitsuParameterModel)
            elif provider == "nec":
                return isinstance(parameter_model, NEC2ParameterModel)
            elif provider == "nec_3":
                return isinstance(parameter_model, NEC3ParameterModel)
            elif provider == "jij":
                if solver == "jij.pysciopt":
                    return isinstance(parameter_model, JijParameterModel)
                else:
                    raise ValueError("Invalid solver")
            elif provider == "braket":
                return isinstance(parameter_model, AquilaParameterModel)
            elif provider == "lightsolver":
                return isinstance(parameter_model, LightSolverParameterModel)
            elif provider == "swfdas":
                return isinstance(parameter_model, FujitsuParameterModel)
            elif provider == "qaoa":
                return isinstance(parameter_model, QAOAParameterModel)
            else:
                raise StrangeworksError(
                    f"Parameter model compatibility check failed due to non-existent provider {provider}"
                )
        else:
            return True

    def get_options(
        self, provider: str, solver: str, solver_options: dict[str, Any]
    ) -> (
        AquilaParameterModel
        | DwaveLeapParameterModel
        | DwaveSamplerParameterModel
        | FujitsuParameterModel
        | GurobiParameterModel
        | HitachiParameterModel
        | JijParameterModel
        | NEC2ParameterModel
        | NEC3ParameterModel
        | QuantagoniaParameterModel
        | ToshibaParameterModel
    ):
        if provider == "dwave":
            if (
                solver == "dwave.hybrid_binary_quadratic_model_version2p"
                or solver == "dwave.hybrid_constrained_quadratic_model_version1p"
                or solver == "dwave.hybrid_discrete_quadratic_model_version1p"
            ):
                return DwaveLeapParameterModel(**solver_options)
            else:
                return DwaveSamplerParameterModel(**solver_options)
        elif provider == "gurobi":
            return GurobiParameterModel(**solver_options)
        elif provider == "quantagonia":
            return QuantagoniaParameterModel(**solver_options)
        elif provider == "hitachi":
            return HitachiParameterModel(**solver_options)
        elif provider == "toshiba":
            return ToshibaParameterModel(**solver_options)
        elif provider == "fujitsu":
            return FujitsuParameterModel(**solver_options)
        elif provider == "nec":
            return NEC2ParameterModel(**solver_options)
        elif provider == "nec_3":
            return NEC3ParameterModel(**solver_options)
        elif provider == "jij":
            if solver == "jij.pysciopt":
                return JijParameterModel(**solver_options)
            else:
                raise ValueError("Invalid solver")
        elif provider == "aquila":
            return AquilaParameterModel(**solver_options)
        else:
            raise ValueError("Invalid provider")

    def results(self, sw_job_slug):
        OptJob = self.download_input_file(sw_job_slug)
        solution = OptJob.solution

        if solution is None or solution.solution == "":
            job = sw.jobs(slug=sw_job_slug)[0]
            status = job.status

            while not status.is_terminal_state:  # COMPLETED, CANCELLED, or FAILED
                time.sleep(10)
                status = self.status(sw_job_slug)

            if status == Status.COMPLETED:
                endpoint = f"results-remote/{sw_job_slug}"
                file_url = sw.execute(self.resource, endpoint=endpoint)
                solution = StrangeworksOptimizationJob(**sw.download_job_files([file_url])[0]).solution
            else:
                try:
                    msg = f"Cannot get results for Job {sw_job_slug}, Job status is {status.value}. \n"
                    error_json = sw.get_error_messages(sw_job_slug)

                    if len(error_json["parent_job"]) == 0:
                        msg += "\nNo Errors associated to parent job, checking child job.\n"
                    else:
                        msg += "\nErrors in parent job: \n\n"
                        for er in error_json["parent_job"]:
                            for key in er.keys():
                                msg += f"Error Type: {key}: "
                                msg += str(er[key])
                                msg += "\n"

                    if len(error_json["child_jobs"]) == 0:
                        msg += "\nNo Errors associated to child jobs.\n"
                    else:
                        msg += "\nErrors in child jobs: \n\n"
                        for er in error_json["child_jobs"]:
                            for key in er.keys():
                                msg += f"Error Type: {key}: "
                                msg += str(er[key])
                                msg += "\n"
                except Exception:
                    msg = f"Cannot get results for Job {sw_job_slug}, Job status is {status.value}. \n"
                    error_json = sw.get_error_messages(sw_job_slug)
                    msg += pprint.pformat(error_json)

                raise StrangeworksError(msg)

        return solution.deserialize()

    def status(self, sw_job_slug) -> Status:
        endpoint = f"status/{sw_job_slug}"
        resp = sw.execute(self.resource, endpoint=endpoint)
        return Status(resp)

    def jobs_by_tag(self, tags: List[str], andor: str = "AND"):
        """
        Return all of the jobs with the given tags

        Parameters
        ----------
        tags: List[str]
            List of tags to filter the jobs by.

        andor: str
            The logical operator to use for the tags. Can be either "AND" or "OR".

        """

        if andor == "AND":
            job_list = [sw.jobs(tags=t) for t in tags]
            slug_list = [[j.slug for j in jobset] for jobset in job_list]

            commonalities = set(slug_list[0])
            for ii in range(1, len(slug_list)):
                commonalities &= set(slug_list[ii])

            all_jobs_flat = [job for sublist in job_list for job in sublist]
            unique_jobs = {job.slug: job for job in all_jobs_flat}.values()

            return [job for job in unique_jobs if job.slug in commonalities]
        elif andor == "OR":
            return sw.jobs(tags=tags)
        else:
            raise ValueError("andor must be either 'AND' or 'OR'")

    def upload_model(self, model, filename: str | None = None, description: str | None = None) -> RemoteFile:
        """
        Uploads the model to Strangeworks and returns the slug of the uploaded file.

        Parameters
        ----------
        model: Any
            The model to be uploaded. This will be parsed into a StrangeworksOptimizationModel.
            To ensure that we support the type, and to make it easy to work with the model on the service side.

        To-Do:
        filename: str (optional)
            The filename to use for the uploaded file. If not provided, a random filename will be used. This will
            make it easier for users to understand what their workspace files are.
        description: str (optional)
            A description of the file to be uploaded. This will be used to help users understand what the file is
            for, and to help them understand what the file is for.

        """
        strangeworks_optimization_model = StrangeworksOptimizationModel.from_model(model=model or self.model)
        # The delete=False here is so that it will work in windows machines. Windows has strange behaviour with
        # the permissions of temporary files which was raising errors when trying to upload the tmp file to sw.
        # See pypa/pip-audit#646 for more details.
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as t:
            t.write(strangeworks_optimization_model.model_dump_json())
            t.flush()

            # To-DO: Add filename, description and info to the upload_file method
            # f = sw.upload_file(
            #     file_path=t.name,
            #     name=filename,
            #     description=description,
            #     info={"model_type": strangeworks_optimization_model.model_type},
            # )
            f = sw.upload_file(t.name)

        try:
            os.remove(t.name)
        except Exception as err:
            logging.debug("Attempted to remove temporary file with os.remove(t.name):")
            logging.debug(err)

        remote_file = RemoteFile(
            model_url=f.url,
            model_type=strangeworks_optimization_model.model_type,
            # model_type=f.info["model_type"],
            # filename=f.file_name,
            # description=f.description,
        )
        return remote_file

    # def get_workspace_files(self, file_slug: str | None = None) -> List[RemoteFile]:
    #     """
    #     Returns a list of all files in the workspace.

    #     if file_slug:
    #         then create RemoteFile object for that file
    #     else:
    #         list all files in workspace with names and descriptions.
    #     """
    #     pass

    def backends(self) -> Optional[Backend]:
        """List of optimization backends."""
        # get resources associated with this workspace
        resources = sw.resources()
        # if workspace has no resources, return an empty list.
        if not resources:
            return []
        # generate list of product slugs to use for filtering backends.
        product_slugs = [x.product.slug for x in resources]
        backends = sw.backends(
            product_slugs=product_slugs,
            backend_type_slugs=["optimization"],
        )

        return backends

    def download_input_file(self, sw_job_slug) -> StrangeworksOptimizationJob:
        # Returns the entire OptimizationJob object/payload
        # If the job has completed, the solution should also be included.

        sw_job = sw.jobs(slug=sw_job_slug)[0]

        for file in sw_job.files:
            if file.file_name == "OptimizationJob.json":
                return StrangeworksOptimizationJob(**sw.download_job_files([file.url])[0])

        raise StrangeworksError("OptimizationJob.json not found in job files")

    def download_input_model(self, sw_job_slug, download_remote=False):
        # Parses the OptimizationJob.json and returns the deserialized model
        # If download_remote is True, and the model is a RemoteFile type
        # then the model will be downloaded from the remote URL

        OptimizationJob = self.download_input_file(sw_job_slug)
        OptimizationModel = OptimizationJob.model.deserialize().model

        if isinstance(OptimizationModel, RemoteFile) and download_remote:
            return (
                StrangeworksOptimizationModel(**sw.download_job_files([OptimizationModel.model_url])[0])
                .deserialize()
                .model
            )

        return OptimizationModel

    def download_input_model_from_url(self, file_url):
        # Downloads the model from the URL and returns the deserialized model

        model = sw.download_job_files([file_url])
        model = StrangeworksOptimizationModel(**model[0]).deserialize()

        return model

    @property
    def resource_slug(self):
        return self.resource.slug
