"""User-facing methods to improve lineage."""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, overload

from airflow.models.taskinstance import TaskInstance

from astro_observe_sdk.utils.airflow import get_task_instance_from_context
from astro_observe_sdk.utils.database import resolve_query_execution_context
from astro_observe_sdk.utils.openlineage import (
    lineage_run_id,
    emit_openlineage_events_for_query,
    emit_openlineage_running_event,
    is_openlineage_enabled,
    Dataset,
)

if TYPE_CHECKING:
    from snowflake.connector.connection import SnowflakeCursor
    from databricks.sql.client import Cursor as DatabricksCursor


log = logging.getLogger(__name__)

_query_counters: dict[str, int] = defaultdict(int)


@overload
def log_query(  # no db_connector: log query_id and dataset lineage retrieved from query_text parsing
    *,
    query_id: str,
    query_text: str,
    query_job_namespace: str,
    default_database: str | None = None,
    default_schema: str | None = None,
) -> None:
    ...


@overload
def log_query(  # with supported db_connector: log everything we can retrieve from just db_connector
    *,
    db_connector: SnowflakeCursor | DatabricksCursor,
    db_connector_extra_args: dict[str, str | bool] | None = None,
) -> None:
    ...


@overload
def log_query(  # no db_connector: log just query_id without dataset lineage retrieved from query_text parsing
    *,
    query_id: str,
    query_job_namespace: str,
) -> None:
    ...


@overload
def log_query(  # no db_connector: log just dataset lineage retrieved from query_text parsing without query_id
    *,
    query_text: str,
    query_job_namespace: str,
    default_database: str | None = None,
    default_schema: str | None = None,
) -> None:
    ...


@overload
def log_query(  # original function signature: all other scenarios described in docstring
    *,
    query_id: str | None = None,
    query_text: str | None = None,
    db_connector: SnowflakeCursor | DatabricksCursor | None = None,
    query_job_namespace: str | None = None,
    db_connector_extra_args: dict[str, str | bool] | None = None,
    default_database: str | None = None,
    default_schema: str | None = None,
    task_instance: TaskInstance | None = None,
) -> None:
    ...


def log_query(
    *,
    query_id: str | None = None,
    query_text: str | None = None,
    db_connector: SnowflakeCursor | DatabricksCursor | None = None,
    query_job_namespace: str | None = None,
    db_connector_extra_args: dict[str, str | bool] | None = None,
    default_database: str | None = None,
    default_schema: str | None = None,
    task_instance: TaskInstance | None = None,
) -> None:
    """Emits OpenLineage events for a given SQL query execution.

    This function captures lineage information, including inputs, outputs, and run metadata,
    by parsing SQL query (provided explicitly by the user or retrieved via the provided database connector).
    By parsing the SQL query and leveraging a query identifier, this function constructs the appropriate
    OpenLineage `job` and `run` facets. It then emits OpenLineage pair (START and COMPLETE/FAIL) events
    directly associated with the corresponding Airflow task run, allowing for detailed visibility into
    which queries were executed as part of each DAG and task execution. The function can be invoked multiple
    times within a single task.

    Function supports two main modes of operation, each designed to cater to different workflows:
    1. Without db_connector provided:
        In this mode, user supplies all required information directly, including query text, query ID,
        query job namespace, and any other relevant metadata.

        When query_id and query_job_namespace are provided, the SDK logs the query_id and associates it
        with the corresponding Airflow task.
        When query_text and query_job_namespace are provided, the SDK performs SQL parsing to identify
        input and output datasets, and associates it with the corresponding Airflow task.

        Key Details:
        - No database calls are made by the SDK.
        - The SDK relies entirely on the provided input data to log the query.
    2. With supported db_connector provided:
        In this mode, user provides a database connector along with any available metadata.
        This function should be called soon after the query completes to ensure all metadata can be retrieved.
        Currently supported are Snowflake and Databricks cursors. For other types of databases, we recommend
        not providing the db_connector and providing all query metadata explicitly.

        Key Details:
        - When required metadata is not provided explicitly by the user, the SDK may call the database to fetch
        query text, query ID, or other execution details. This can modify the db_connector (e.g., last query ID).
        - To ensure the db_connector is used only to read its existing attributes and makes no additional database
        calls, set `offline_mode: True` in `db_connector_extra_args`. In this mode, provide all possible metadata
        to the log_query method to prevent errors caused by missing information.
        - For Snowflake, the SDK only retrieves query text and execution metadata for queries that completed within
         the last 5 minutes (default) to avoid costly scans of the large QUERY_HISTORY table. This time window can
         be adjusted using the `query_history_lookback_minutes` parameter in `db_connector_extra_args` arg.
         When specified, queries outside this window or still running will not return metadata. Use `0` for no limit
         or filters on query state. For Databricks, there is currently no time restriction.


    Args:
        query_id: A unique identifier for the query in given query_job_namespace e.g. snowflake account.
        query_text: The raw SQL query text, used to extract input/output datasets by SQL parsing.
        db_connector: Cursor from supported database, used to execute queries and retrieve query metadata.
        query_job_namespace: The OpenLineage namespace for the query job, including the system type prefix,
        e.g., ``"snowflake://org_id-acc_id"``, ``"databricks://adb-<id>.azuredatabricks.net"``, ``bigquery``.
        db_connector_extra_args: Additional parameters to facilitate metadata extraction. Accepted parameters:
         For all type of db_connectors:
         - offline_mode: bool - If the db_connector should only be used to extract its existing attributes
          and should not perform any additional database calls. Default value is False which means db_connector
          is allowed to make external calls e.g., using its .execute() method.

        For Snowflake Cursor:
         - account_id: str (example: "FY00763-GP86231") - Snowflake account identifier
         - query_history_lookback_minutes: int (example: 10, default: 5) - Restricts query metadata lookup to
          queries completed within the last N minutes. Use `0` for no limit or filters on query state.

        For Databricks Cursor:
         - host: str (example: "adb-123.10.azuredatabricks.net") - Databricks host
         - token: str (example: "dapi2e23c871e9x8942f5a0bxcf1d4a0dd88-3") - Databricks PAT
        default_database: Default database to resolve unqualified table references in query_text.
        default_schema: Default schema to resolve unqualified table references in query_text.
        task_instance: Airflow task instance associated with the query execution.
         If not provided, it will be derived from the task execution context.

    Raises:
        1. ValueError: If ``query_job_namespace`` is not provided.
        >>> log_query(
        ...     query_id="acde070d-8c4c-4f0d-9d8a-162843c10333",
        ... )
        or if by any reason ``query_job_namespace`` could not be extracted from db_connector
        >>> log_query(
        ...     db_connector="<SnowflakeCursor or DatabricksCursor instance>",
        ... )

        2. ValueError: If neither ``query_id`` nor ``query_text`` is provided explicitly.
        >>> log_query(
        ...     query_job_namespace="databricks://adb-498971240325220.10.azuredatabricks.net",
        ... )
        or if db_connector only is provided, but it does not contain last query_id within its attributes.
        >>> log_query(
        ...     db_connector="<SnowflakeCursor or DatabricksCursor instance>",
        ... )

    Examples:
        1. Log a query using a query ID
         In this scenario, only the query_id and the query_job_namespace are provided. Since no query_text
         is available, dataset lineage extraction (inputs/outputs) from SQL parsing cannot be performed.

         The function will emit OpenLineage events that include the query_id, identifying the executed query
         within the given query_job_namespace (e.g., Snowflake account). That metadata can be later used by Observe
         to attribute given query id to a specific Airflow task run.
        >>> log_query(
        ...     query_id="acde070d-8c4c-4f0d-9d8a-162843c10333",
        ...     query_job_namespace="databricks://adb-498971240325220.10.azuredatabricks.net",
        ... )

        2. Log a query using SQL text
         In this scenario, the SQL query is provided through query_text, along with the required query_job_namespace.
         No query_id is specified.

         The function will:
         - Parse the SQL from query_text to extract input and output datasets (lineage).
         - Use default_database and default_schema (if provided) to resolve unqualified table names.
         - Emit OpenLineage events that contain dataset lineage, but no query_id.

         Since no query_id is included, the emitted OpenLineage events cannot be linked back to a specific database
         query execution, but they will accurately reflect the datasets referenced in the SQL statement that can
         be later used by Observe to attribute to a specific Airflow task run.
        >>> log_query(
        ...     query_text="SELECT * FROM users",
        ...     query_job_namespace="snowflake://FY01283-GP92841",
        ...     default_database="analytics",
        ...     default_schema="public",
        ... )

        3. Log a query using SQL text and query ID
         In this scenario, both the SQL text and the query_id are provided, along with query_job_namespace.

         The function will:
         - Parse the SQL from query_text to extract input and output datasets (lineage).
         - Use default_database and default_schema (if provided) to resolve unqualified table names.
         - Include the provided query_id in the emitted OpenLineage events to uniquely identify the query execution.

         This produces the most complete form of logging as OpenLineage events will contain both dataset lineage
         and query_id, enabling accurate attribution of lineage and query run to Airflow task run.
        >>> log_query(
        ...     query_id="bquxjob_69ed4f1_169ba1f5665",
        ...     query_text="SELECT * FROM users",
        ...     query_job_namespace="bigquery",
        ...     default_database="my-project",
        ...     default_schema="my-dataset",
        ... )

        4. Log a query using just supported db_connector (Snowflake or Databricks cursor)
         In this scenario, only a db_connector is provided. The expectation is that the cursor has already
         executed at least one query prior to calling `log_query` (so it contains last query_id).

         The function will attempt to infer all required metadata directly from the db_connector and, if necessary,
         by making additional calls to the database. This includes:
          - query_id — retrieved from the cursor’s attributes as the identifier of the most recently executed query.
          - query_text — fetched via a database call if supported by the connector.
          - query_job_namespace — derived from cursor attributes (e.g., Snowflake account, Databricks host),
            or retrieved via a database call if not present on the cursor.
          - default_database and default_schema — obtained from the cursor’s attributes when available,
            or retrieved via a database call if supported and not present on the cursor.

         If all metadata is found, this can produce the most complete form of logging as OpenLineage events will
         contain both dataset lineage and query_id, enabling accurate attribution of query run to Airflow task run.

         Note: If required metadata such as query_id or query_text and query_job_namespace cannot be inferred from
         the connector or database call, a ValueError will be raised.

         We always recommend providing as much metadata as possible explicitly and not relying on cursor object.
        >>> log_query(
        ...     db_connector="<SnowflakeCursor or DatabricksCursor instance>",
        ... )

        5. Log a query using db_connector, some metadata and force lack of extra calls made by db_connector
         In this scenario, a db_connector is provided along with some metadata (such as query_id and/or query_text).
         However, the user sets offline_mode=True in db_connector_extra_args, which instructs the `log_query` not to
         make additional database calls and only retrieve information from db_connector attributes in an offline way.

         The function will:
          - Use only the explicitly provided arguments and metadata available directly on the cursor object
           (host, token, query_job_namespace and default database/schema).
          - Not call the database to retrieve query_text, query_job_namespace, default_database, or default_schema.

         Note: If required query_job_namespace cannot be inferred from the connector, a ValueError will be raised.

         This mode is useful when:
          - Database access is restricted or undesirable (e.g., audit/security constraints).
          - You want reproducible lineage logging without relying on dynamic database state.

         We always recommend providing as much metadata as possible explicitly and not relying on cursor object.
        >>> log_query(
        ...     db_connector="<DatabricksCursor instance>",
        ...     db_connector_extra_args={"offline_mode": True},  # offline_mode works for any type of db_connector
        ...     query_text="SELECT * FROM users",
        ...     query_id="acde070d-8c4c-4f0d-9d8a-162843c10333",
        ... )

        6.1 Log a query using just Databricks db_connector with explicit token and host
         In this scenario, only a Databricks cursor (db_connector) is provided, but the user also supplies
         host and token via db_connector_extra_args. This reduces the chance of failure in cases where the cursor
         does not expose enough metadata to construct the query_job_namespace or authenticate for database calls.
        >>> log_query(
        ...     db_connector="<DatabricksCursor instance>",
        ...     db_connector_extra_args={"host": "adb-498971240325220.10.azuredatabricks.net", "token": "123"},
        ... )

        6.2 Log a query using just Snowflake db_connector with explicit account_id
         In this scenario, only a Snowflake cursor (db_connector) is provided, along with an explicit account_id.
         This reduces the chance of failure in cases where the cursordoes not expose enough metadata to construct
         the query_job_namespace or authenticate for database calls. The query_history_lookback_minutes parameter
         is also used to limit metadata retrieval to queries that completed within the last N minutes, helping
         reduce query time when scanning Snowflake’s QUERY_HISTORY table.

         query_history_lookback_minutes is also provided
         to only look for query metadata within last two minutes of query_history table to reduce query time.
        >>> log_query(
        ...     db_connector="<SnowflakeCursor instance>",
        ...     db_connector_extra_args={"account_id": "FY01283-GP92841", "query_history_lookback_minutes": 2},
        ... )

        6.3 Log a query using db_connector, query_job_namespace and query_id
         In this scenario, the user provides the db_connector along with explicit query_job_namespace and query_id.
         The function does not need to extract the query ID from the cursor, but it may still make database calls
         to retrieve missing information such as query_text, default_database, or default_schema.
        >>> log_query(
        ...     db_connector="<DatabricksCursor instance>",
        ...     query_job_namespace="databricks://adb-498971240325220.10.azuredatabricks.net",
        ...     query_id="acde070d-8c4c-4f0d-9d8a-162843c10333",
        ... )

        6.4 Log a query using db_connector and query_job_namespace:
         In this scenario, the user provides a db_connector and explicitly sets query_job_namespace, but leaves
         query_id and query_text to be retrieved automatically. The function will:
          - Retrieve the query_id from the cursor (last executed query),
          - Fetch the query_text and default database/schema from the database (if supported),
          - Then emit OpenLineage events with all information retrieved

         Note: If required metadata such as query_id or query_text cannot be inferred from
         the connector or database call, a ValueError will be raised.
        >>> log_query(
        ...     db_connector="<SnowflakeCursor instance>",
        ...     query_job_namespace="snowflake://FY01283-GP92841",
        ... )

        6.5 Log a query using db_connector and query_text:
        In this scenario, the user provides a db_connector and an explicit query_text, but does not specify query_id.
        The function will:
          - Retrieve the query_id from the cursor (last executed query),
          - Use the provided query_text to extract dataset lineage.
          - Attempt to infer query_job_namespace, default_database, and default_schema from the connector or
            database calls if needed.
          - Then emit OpenLineage events with all information retrieved

        Note: If required query_job_namespace cannot be inferred from the connector or database call,
         a ValueError will be raised.
        >>> log_query(
        ...     db_connector="<DatabricksCursor instance>",
        ...     query_text="SELECT * FROM users",
        ... )

        7. Log a query using db_connector and all other metadata
         In this scenario, the user provides all available metadata directly: query_id, query_text, query_job_namespace,
         default_database, and default_schema—along with a db_connector. Because no additional information needs
         to be inferred, the function will not use the db_connector to make any database calls.
         It will rely entirely on the provided parameters to construct and emit OpenLineage events, so it's
         an equivalent to example scenario number 3.
        >>> log_query(
        ...     db_connector="<DatabricksCursor instance>",
        ...     db_connector_extra_args={"host": "adb-498971240325220.10.azuredatabricks.net", "token": "123"},
        ...     query_job_namespace="databricks://adb-498971240325220.10.azuredatabricks.net",
        ...     query_text="SELECT * FROM users",
        ...     default_database="mydb",
        ...     default_schema="myschema",
        ...     query_id="acde070d-8c4c-4f0d-9d8a-162843c10333",
        ... )

        8. Log multiple queries
         In this scenario a function is called multiple times within single Airflow task.
        >>> # cursor.execute("<first query>")
        >>> log_query(
        ...     db_connector="<cursor>",
        ...     db_connector_extra_args={"host": "adb-498971240325220.10.azuredatabricks.net", "token": "123"},
        ... )
        >>> # cursor.execute("<second query>")
        >>> log_query(
        ...     db_connector="<cursor>",
        ...     db_connector_extra_args={"host": "adb-498971240325220.10.azuredatabricks.net", "token": "123"},
        ... )
    """
    log.debug("Observe SDK `log_query` has been called.")

    if not is_openlineage_enabled():
        log.info("OpenLineage is disabled - the Observe SDK’s `log_query` call will have no effect.")
        return

    if task_instance is None:
        log.debug("TaskInstance not provided, retrieving it from context.")
        task_instance = get_task_instance_from_context()

    ctx = resolve_query_execution_context(
        query_id=query_id,
        query_text=query_text,
        db_connector=db_connector,
        query_job_namespace=query_job_namespace,
        default_database=default_database,
        default_schema=default_schema,
        db_connector_extra_args=db_connector_extra_args,
    )

    ti_key = lineage_run_id(task_instance)
    _query_counters[ti_key] += 1

    emit_openlineage_events_for_query(
        query_number=_query_counters[ti_key],
        task_instance=task_instance,
        query_id=ctx.query_id,
        query_text=ctx.query_text,
        default_database=ctx.default_database,
        default_schema=ctx.default_schema,
        query_namespace=ctx.query_job_namespace,
        db_type=ctx.db_type,
        error=ctx.query_execution_metadata.error,
        start_time=ctx.query_execution_metadata.start_time,
        end_time=ctx.query_execution_metadata.end_time,
        is_successful=ctx.query_execution_metadata.is_successful,
    )


def log_lineage(
    *,
    inputs: list[Dataset] | None = None,
    outputs: list[Dataset] | None = None,
    task_instance: TaskInstance | None = None,
) -> None:
    """Emits OpenLineage RUNNING event with provided lineage information.

    This function captures and emits dataset lineage information (inputs and outputs) for an Airflow task run
    by emitting an OpenLineage RUNNING event. The function directly accepts OpenLineage Dataset objects
    representing input and output datasets, constructs a RUNNING event, associates it with the corresponding
    Airflow task run, and emits it through the OpenLineage adapter. This allows Observe to track dataset
    dependencies for the task execution. The function can be called multiple times within a single task.

    Important References:
    - Dataset naming convention: https://openlineage.io/docs/spec/naming
    - Available dataset facets: https://openlineage.io/docs/spec/facets/dataset-facets/

    Args:
        inputs: List of OpenLineage Dataset objects representing input datasets consumed by the task.
            At least one of `inputs` or `outputs` must be provided (both cannot be empty).
        outputs: List of OpenLineage Dataset objects representing output datasets produced by the task.
            At least one of `inputs` or `outputs` must be provided (both cannot be empty).
        task_instance: Airflow task instance associated with the lineage logging.
            If not provided, it will be derived from the task execution context.

    Raises:
        1. ValueError: If both `inputs` and `outputs` are None or empty.
        2. TypeError: If any item in `inputs` or `outputs` is not an OpenLineage Dataset object.

    Examples:
        1. Log inputs and outputs
           In this scenario a single input and multiple outputs are provided, including file-based operations.

           The function will emit a RUNNING event that includes both input and output datasets, establishing
           a complete lineage relationship for the task execution.
           >>> from openlineage.client.event_v2 import Dataset
           >>> log_lineage(
           ...     inputs=[
           ...         Dataset(namespace="s3://bucket", name="raw-data/2024/01/01/data.csv", facets={}),
           ...     ],
           ...     outputs=[
           ...         Dataset(namespace="snowflake://account", name="analytics.public.users_processed", facets={}),
           ...         Dataset(namespace="snowflake://account", name="analytics.public.users_summary", facets={}),
           ...         Dataset(namespace="s3://bucket", name="processed-data/2024/01/01/data.parquet", facets={}),
           ... )

        2. Log lineage with facets
           In this scenario, datasets include facets - metadata such as schema details, data quality metrics,
           or other custom information - that enrich the lineage with additional context.

           >>> from openlineage.client.event_v2 import Dataset
           >>> from openlineage.client.facet_v2 import schema_dataset
           >>> schema_facet = schema_dataset.SchemaDatasetFacet(
           ...     fields=[
           ...         schema_dataset.SchemaDatasetFacetFields(name="id", type="INTEGER"),
           ...         schema_dataset.SchemaDatasetFacetFields(name="name", type="VARCHAR"),
           ...     ]
           ... )
           >>> log_lineage(
           ...     inputs=[
           ...         Dataset(
           ...             namespace="snowflake://account",
           ...             name="analytics.public.users",
           ...             facets={"schema": schema_facet},
           ...         ),
           ...     ],
           ...     outputs=[
           ...         Dataset(
           ...             namespace="snowflake://account",
           ...             name="analytics.public.users_processed",
           ...             facets={"schema": schema_facet},
           ...         ),
           ...     ],
           ... )
    """
    log.debug("Observe SDK `log_lineage` has been called.")

    if not is_openlineage_enabled():
        log.info("OpenLineage is disabled - the Observe SDK’s `log_lineage` call will have no effect.")
        return

    if not inputs and not outputs:
        raise ValueError("Either `inputs` or `outputs` must be provided.")

    inputs = inputs or []
    outputs = outputs or []
    if not all([isinstance(x, Dataset) for x in inputs + outputs]):
        raise TypeError("Only OpenLineage Datasets are accepted as inputs/outputs.")

    if task_instance is None:
        log.debug("TaskInstance not provided, retrieving it from context.")
        task_instance = get_task_instance_from_context()

    emit_openlineage_running_event(
        task_instance=task_instance,
        inputs=inputs,
        outputs=outputs,
    )
