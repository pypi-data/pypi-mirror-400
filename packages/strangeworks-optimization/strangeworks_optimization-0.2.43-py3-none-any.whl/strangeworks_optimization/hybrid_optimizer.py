import copy
import json
from typing import Any, List

import strangeworks as sw
from strangeworks.core.client.jobs import Job
from strangeworks.core.errors.error import StrangeworksError
from strangeworks_optimization_models.parameter_models import SWHybridParameterModel
from strangeworks_optimization_models.solver_models import StrangeworksSolverFactory
from strangeworks_optimization_models.strangeworks_models import (
    StrangeworksOptimizationJob,
    StrangeworksOptimizationModel,
    StrangeworksOptimizationSolution,
    StrangeworksOptimizationSolver,
)

from strangeworks_optimization.optimizer import StrangeworksOptimizer, _get_product_slug


class StrangeworksHybridOptimizer(StrangeworksOptimizer):
    """Strangeworks optimization controller."""

    def __init__(
        self,
        model: Any | None = None,
        solver: List[Any] | None = None,
        options: SWHybridParameterModel | None = None,
        solution: Any | None = None,
        resource_slug: str | None = None,
        tags: List[str] | None = None,
    ) -> None:
        super().__init__(model=model, solution=solution, resource_slug=resource_slug, tags=tags)

        self.hybrid_options = options if options else SWHybridParameterModel()

        if solver:
            self.hybrid_solvers = {}
            for sol in solver:
                self.hybrid_solvers[sol] = StrangeworksSolverFactory.from_solver(sol)
            self._init_hybrid_solvers()

    def _init_hybrid_solvers(self):
        if self.hybrid_solvers:
            for solver in self.hybrid_solvers:
                product_slug = _get_product_slug(self.hybrid_solvers[solver].provider)
                self.sub_rsc = sw.get_resource_for_product(product_slug)

                self.hybrid_solvers[solver].strangeworks_parameters = {
                    "sub_product_slug": self.sub_rsc.product.slug,
                    "sub_resource_slug": self.sub_rsc.slug,
                }

    def run(self) -> Job | None:
        for sol in self.hybrid_solvers:
            solver_model = self.hybrid_solvers[sol]

            solver = StrangeworksOptimizationSolver.from_solver(solver_model)
            if (
                self.hybrid_options
                and self.hybrid_options.sampler_parameters
                and self.hybrid_options.sampler_parameters.get(sol)
            ):
                if not self.check_parameter_model_compatibility(
                    solver.solver.split(".", 1)[0], solver_model.solver, self.hybrid_options.sampler_parameters[sol]
                ):
                    raise StrangeworksError(
                        f"Parameter option {self.hybrid_options.sampler_parameters[sol]} is not compatible with {solver.solver}"
                    )
            elif self.hybrid_options:
                if not self.hybrid_options.sampler_parameters:
                    self.hybrid_options.sampler_parameters = {}
                self.hybrid_options.sampler_parameters[sol] = None

        if self.hybrid_options:
            # Transform options class to dict and remove entries that are None
            self.hybrid_options.serialize_options()
            options = copy.deepcopy(self.hybrid_options.__dict__)
            for k, v in self.hybrid_options.__dict__.items():
                if v is None:
                    options.pop(k)

        hybrid_solver = StrangeworksSolverFactory.from_solver("sw_hybrid.sw_hybrid_solver")
        hybrid_solver.strangeworks_parameters = {}
        for sol in self.hybrid_solvers:
            hybrid_solver.strangeworks_parameters[sol] = self.hybrid_solvers[sol].strangeworks_parameters

        hybrid_solver = StrangeworksOptimizationSolver.from_solver(hybrid_solver)
        hybrid_solver.solver_options = json.dumps(options) if self.hybrid_options else json.dumps(None)

        if self.tags:
            for tag in self.tags:
                if len(tag) > 35:
                    raise StrangeworksError("Tag length cannot be greater than 35 characters")

            sw_params = json.loads(hybrid_solver.strangeworks_parameters)
            if sw_params:
                sw_params["tags"] = self.tags
            else:
                sw_params = {"tags": self.tags}
            hybrid_solver.strangeworks_parameters = json.dumps(sw_params)

        strangeworks_optimization_job = StrangeworksOptimizationJob(
            model=StrangeworksOptimizationModel.from_model(self.model),
            solver=hybrid_solver,
            solution=StrangeworksOptimizationSolution.from_solution(self.solution) if self.solution else None,
        )
        res = sw.execute(self.resource, payload=strangeworks_optimization_job.model_dump(), endpoint="run-hybrid")

        job_slug = json.loads(res["solution"]["strangeworks_parameters"])["job_slug"]
        self.job = sw.jobs(slug=job_slug)[0]
        return self.job
