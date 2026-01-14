# observe-sdk

An Airflow and Python SDK for working with the Astro Observe platform

## Installation

Add the following to `requirements.txt`:

```text
astro-observe-sdk>=0.0.8
```

## Usage

### Metrics

The Observe SDK allows user to emit metrics during Airflow task execution to get tracked in the Observe backend. To do so, use the `astro_observe_sdk.log_metric` function like so:

```python
import astro_observe_sdk as observe

# then, in the task
@task
def my_task():
    observe.log_metric('my_metric', 42)
```

### Capture Lineage from SQL Queries

The Observe SDK provides functionality for logging query executions during Airflow task runs, 
enabling the tracking of table/dataset lineage in the Observe backend.

The primary entry point is the `astro_observe_sdk.log_query` function. 
This function captures lineage information, including inputs, outputs, and run metadata, 
by parsing SQL query (provided explicitly by the user or retrieved via the provided database connector). 
By parsing the SQL query and leveraging a query identifier, this function constructs the appropriate OpenLineage `job` and `run` facets. 
It then emits OpenLineage pair (START and COMPLETE/FAIL) events directly associated with the corresponding Airflow task run, 
allowing for detailed visibility into which queries were executed as part of each DAG and task execution.
The function can be invoked multiple times within a single task.

User can call log_query in several ways, depending on how much metadata is available.  

**Please refer to `astro_observe_sdk.log_query` function's docstring for a detailed guide and additional examples.**

1. Log using query metadata:
```python
import astro_observe_sdk as observe

@task
def my_task():
    observe.log_query(
        query_job_namespace="bigquery",
        query_text="SELECT a, b, c FROM users",
        default_database="my_project",
        default_schema="my_dataset",
        query_id="bquxjob_69ed4f1_169ba1f5665",
    )
```

2. Log using just supported DB connector (Snowflake or Databricks cursor):
```python
import astro_observe_sdk as observe
from databricks import sql

@task
def my_task():
    conn = sql.connect(
        server_hostname="adb-123.10.azuredatabricks.net",
        access_token="secret-token",
        http_path="/sql/1.0/warehouses/abc123",
    )
    cs = conn.cursor()
    cs.execute("SELECT * FROM `test`.some_schema.table1;")
    
    observe.log_query(
        db_connector=cs,
        # We try to retrieve the below from cursor object if not provided, but we highly recommend passing it explicitly
        db_connector_extra_args={"host": "adb-123.10.azuredatabricks.net", "token": "secret-token"}
    )
```

### Capture Lineage from Datasets

The Observe SDK also provides functionality for logging dataset lineage directly, without requiring SQL query parsing. 
The primary entry point is the `astro_observe_sdk.log_lineage` function. 
This function accepts OpenLineage Dataset objects representing input and output datasets, and emits a RUNNING event 
directly associated with the corresponding Airflow task run.

**Please refer to `astro_observe_sdk.log_lineage` function's docstring for a detailed guide and additional examples.**

1. Simple lineage logging:
```python
import astro_observe_sdk as observe
from openlineage.client.event_v2 import Dataset

@task
def my_task():
    observe.log_lineage(
        inputs=[
            Dataset(namespace="snowflake://account", name="analytics.public.users", facets={}),
        ],
        outputs=[
            Dataset(namespace="snowflake://account", name="analytics.public.users_processed", facets={}),
        ],
    )
```

2. Lineage logging with facets (metadata):
```python
import astro_observe_sdk as observe
from openlineage.client.event_v2 import Dataset
from openlineage.client.facet_v2 import schema_dataset

@task
def my_task():
    schema_facet = schema_dataset.SchemaDatasetFacet(
        fields=[
            schema_dataset.SchemaDatasetFacetFields(name="id", type="INTEGER"),
            schema_dataset.SchemaDatasetFacetFields(name="name", type="VARCHAR"),
        ]
    )
    observe.log_lineage(
        inputs=[
            Dataset(
                namespace="snowflake://account",
                name="analytics.public.users",
                facets={"schema": schema_facet},
            ),
        ],
        outputs=[
            Dataset(
                namespace="snowflake://account",
                name="analytics.public.users_processed",
                facets={"schema": schema_facet},
            ),
        ],
    )
```

### Choosing Between `log_query` and `log_lineage`

Both `log_query` and `log_lineage` enable lineage tracking, but they serve different use cases:

**Use `log_query` when:**
- You have SQL queries and want automatic parsing to extract dataset lineage.
- You're working with supported database connectors (Snowflake, Databricks) and want automatic metadata retrieval.
- You want to track query execution metadata (query ID, query_text, execution time, status).

**Use `log_lineage` when:**
- You already have dataset lineage information (e.g., from file operations, APIs, or custom logic).
- You're working with non-SQL data transformations or operations that don't involve SQL queries.
- You want full control over the exact datasets and metadata included in the lineage event.

In summary: `log_query` is ideal for SQL-based workflows where you want automatic parsing and complete lifecycle tracking, 
while `log_lineage` is better for operations when you already have explicit dataset information.
