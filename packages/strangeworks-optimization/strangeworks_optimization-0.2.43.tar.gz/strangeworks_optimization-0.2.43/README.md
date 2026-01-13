![Tests](https://github.com/strangeworks/strangeworks-optimization/actions/workflows/cron_test.yml/badge.svg)

# strangeworks-optimization

[Docs](https://docs.strangeworks.com/apps/optimization)


## Usage

```python
# model has been created and is one of the StrangeworksModelTypes
model = ...
solver = "my_provider.my_solver"
optimizer = StrangeworksOptimizer(model, solver)
optimizer.run()
print(optimizer.status())
print(optimizer.results())
```

### Dev notes

```bash
gcloud beta logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=svc-optimization severity>=ERROR"
gcloud beta logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=svc-dwave-prod"


resource.type = "cloud_run_revision"
resource.labels.service_name = "svc-optimization"
resource.labels.location = "us-central1"
 severity>=DEFAULT
-textPayload NOT "job_updater|sw-optimization-service"
```
