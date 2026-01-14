"""OpenLineage related internal utilities."""
import logging
from datetime import datetime, timezone

from airflow.models.taskinstance import TaskInstance
from airflow.providers.openlineage.plugins.listener import get_openlineage_listener
from airflow.providers.openlineage.plugins.macros import (
    lineage_run_id,
    lineage_job_name,
    lineage_job_namespace,
)
from airflow.providers.openlineage.sqlparser import SQLParser, from_table_meta
from openlineage.client.event_v2 import Dataset, RunEvent, Job, Run, RunState
from openlineage.client.facet_v2 import (
    external_query_run,
    sql_job,
    job_type_job,
    JobFacet,
    RunFacet,
    parent_run,
    error_message_run,
)
from openlineage.client.uuid import generate_new_uuid

from astro_observe_sdk.constants import OPENLINEAGE_PRODUCER, AIRFLOW_V_3_0_PLUS

log = logging.getLogger(__name__)


def is_openlineage_enabled() -> bool:
    """
    Check if the OpenLineage provider is accessible.

    This function attempts to import the necessary OpenLineage modules and checks if the provider
    is enabled and the listener is available.

    Returns:
        bool: True if the OpenLineage provider is accessible, False otherwise.
    """
    try:
        from airflow.providers.openlineage.conf import is_disabled
        from airflow.providers.openlineage.plugins.listener import get_openlineage_listener
    except (ImportError, AttributeError):
        log.debug("OpenLineage provider could not be imported.")
        return False

    if is_disabled():
        log.debug("OpenLineage provider is disabled.")
        return False

    if not get_openlineage_listener():
        log.debug("OpenLineage listener could not be found.")
        return False

    return True


def parse_sql(
    query_text: str,
    query_namespace: str,
    default_schema: str | None = None,
    default_database: str | None = None,
    sql_parser_type: str = "default",
    query_dialect: str = "generic",
) -> tuple[list[Dataset], list[Dataset]]:
    """Get inputs and outputs from sql text."""
    log.debug("Using `%s` sql parser.", sql_parser_type)
    if sql_parser_type == "default":
        return _parse_sql_default_parser(
            query_text=query_text,
            query_namespace=query_namespace,
            default_schema=default_schema,
            default_database=default_database,
            query_dialect=query_dialect,
        )
    raise NotImplementedError("Support for other SQL parsers is not implemented yet.")


def _parse_sql_default_parser(
    query_text: str,
    query_namespace: str,
    default_schema: str | None = None,
    default_database: str | None = None,
    query_dialect: str = "generic",
) -> tuple[list[Dataset], list[Dataset]]:
    """Get inputs and outputs from sql text using default OL sqlparser."""
    supported_dialects = (
        "bigquery",
        "databricks",
        "snowflake",
        "postgres",
        "postgresql",
        "redshift",
        "hive",
        "mysql",
        "mssql",
        "sqlite",
        "ansi",
        "generic",
    )
    query_dialect = query_dialect if query_dialect in supported_dialects else "generic"
    sql_parser = SQLParser(dialect=query_dialect, default_schema=default_schema)
    parse_result = sql_parser.parse(sql_parser.split_sql_string(query_text))
    if not parse_result:
        log.debug("Sql parsing produced no input or output datasets.")
        return [], []

    inputs = [
        from_table_meta(dataset, default_database, query_namespace, False)
        for dataset in parse_result.in_tables
    ]
    outputs = [
        from_table_meta(dataset, default_database, query_namespace, False)
        for dataset in parse_result.out_tables
    ]
    log.debug("Sql parsing produced the following: inputs=%s ; outputs=%s", str(inputs), str(outputs))
    return inputs, outputs


def get_parent_run_facet_with_task_as_parent(
    task_instance: TaskInstance,
) -> dict[str, parent_run.ParentRunFacet]:
    """Get parentRunFacet pointing to Airflow task instance as parent."""

    return {
        "parent": parent_run.ParentRunFacet(
            run=parent_run.Run(runId=lineage_run_id(task_instance)),
            job=parent_run.Job(
                namespace=lineage_job_namespace(),
                name=lineage_job_name(task_instance),
            ),
            producer=OPENLINEAGE_PRODUCER,
        )
    }


def get_parent_run_facet_with_dag_as_parent(
    task_instance: TaskInstance,
) -> dict[str, parent_run.ParentRunFacet]:
    """Get parentRunFacet pointing to Airflow DAG instance as parent."""

    from airflow.providers.openlineage.plugins.adapter import OpenLineageAdapter

    if AIRFLOW_V_3_0_PLUS:
        dagrun = task_instance.get_template_context()["dag_run"]
    else:
        dagrun = task_instance.dag_run

    date = dagrun.logical_date
    if AIRFLOW_V_3_0_PLUS and date is None:
        date = dagrun.run_after

    clear_number = getattr(dagrun, "clear_number", 0)

    dag_id = task_instance.dag_id
    try:  # Logic for parent_id changed over time, depending on OL provider version
        parent_run_id = OpenLineageAdapter.build_dag_run_id(
            dag_id=dag_id,
            logical_date=date,  # type: ignore[call-arg]
            clear_number=clear_number,  # type: ignore[call-arg]
        )
    except TypeError:
        try:
            parent_run_id = OpenLineageAdapter.build_dag_run_id(
                dag_id=dag_id,
                logical_date=dagrun.logical_date,  # type: ignore[call-arg]
            )
        except TypeError:
            parent_run_id = OpenLineageAdapter.build_dag_run_id(
                dag_id=dag_id,
                execution_date=dagrun.execution_date,
            )

    return {
        "parent": parent_run.ParentRunFacet(
            run=parent_run.Run(runId=parent_run_id),
            job=parent_run.Job(namespace=lineage_job_namespace(), name=dag_id),
            producer=OPENLINEAGE_PRODUCER,
        )
    }


def get_airflow_run_facet(task_instance: TaskInstance) -> dict:
    from airflow.providers.openlineage.utils.utils import get_airflow_run_facet

    if AIRFLOW_V_3_0_PLUS:
        context = task_instance.get_template_context()
        task = context["task"]
        dagrun = context["dag_run"]
        dag = context["dag"]
    else:
        dagrun = task_instance.dag_run
        task = task_instance.task  # type: ignore[assignment]
        dag = task.dag

    return get_airflow_run_facet(
        dag_run=dagrun,  # type: ignore[arg-type]
        dag=dag,
        task_instance=task_instance,
        task=task,
        task_uuid=lineage_run_id(task_instance),
    )


def create_ol_event_pair(
    job_name: str,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    is_successful: bool = True,
    inputs: list[Dataset] | None = None,
    outputs: list[Dataset] | None = None,
    run_facets: dict | None = None,
    job_facets: dict | None = None,
) -> tuple[RunEvent, RunEvent]:
    """Create a pair of OpenLineage RunEvents representing the start and end of a query execution."""

    run = Run(runId=str(generate_new_uuid()), facets=run_facets or {})
    job = Job(namespace=lineage_job_namespace(), name=job_name, facets=job_facets or {})

    now = datetime.now(tz=timezone.utc)
    if not start_time:
        start_time = now
    if not end_time:
        end_time = now

    start = RunEvent(
        eventType=RunState.START,
        eventTime=start_time.isoformat(),
        run=run,
        job=job,
        inputs=inputs or [],  # type: ignore[arg-type]
        outputs=outputs or [],  # type: ignore[arg-type]
        producer=OPENLINEAGE_PRODUCER,
    )
    end = RunEvent(
        eventType=RunState.COMPLETE if is_successful else RunState.FAIL,
        eventTime=end_time.isoformat(),
        run=run,
        job=job,
        inputs=inputs or [],  # type: ignore[arg-type]
        outputs=outputs or [],  # type: ignore[arg-type]
        producer=OPENLINEAGE_PRODUCER,
    )
    return start, end


def create_ol_running_event(
    run_id: str,
    job_name: str,
    job_namespace: str,
    inputs: list[Dataset] | None = None,
    outputs: list[Dataset] | None = None,
    run_facets: dict | None = None,
    job_facets: dict | None = None,
) -> RunEvent:
    """Create OpenLineage RUNNING event."""

    run = Run(runId=run_id, facets=run_facets or {})
    job = Job(namespace=job_namespace, name=job_name, facets=job_facets or {})

    return RunEvent(
        eventType=RunState.RUNNING,
        eventTime=datetime.now(tz=timezone.utc).isoformat(),
        run=run,
        job=job,
        inputs=inputs or [],  # type: ignore[arg-type]
        outputs=outputs or [],  # type: ignore[arg-type]
        producer=OPENLINEAGE_PRODUCER,
    )


def create_run_facets(
    query_id: str | None = None,
    query_namespace: str | None = None,
    error: str | None = None,
) -> dict[str, RunFacet]:
    """Create run facets for OpenLineage event"""
    run_facets: dict[str, RunFacet] = {}
    if query_id and query_namespace:
        run_facets["externalQuery"] = external_query_run.ExternalQueryRunFacet(
            externalQueryId=query_id, source=query_namespace, producer=OPENLINEAGE_PRODUCER
        )
    if error:
        run_facets["errorMessage"] = error_message_run.ErrorMessageRunFacet(
            message=error, programmingLanguage="SQL", producer=OPENLINEAGE_PRODUCER
        )

    return run_facets


def create_job_facets(
    integration_name: str, job_type: str, query_text: str | None = None
) -> dict[str, JobFacet]:
    """Create run facets for OpenLineage event"""
    job_facets: dict[str, JobFacet] = {
        "jobType": job_type_job.JobTypeJobFacet(
            jobType=job_type.upper(),
            integration=integration_name.upper(),
            processingType="BATCH",
            producer=OPENLINEAGE_PRODUCER,
        )
    }
    if query_text:
        job_facets["sql"] = sql_job.SQLJobFacet(query=query_text, producer=OPENLINEAGE_PRODUCER)

    return job_facets


def emit_openlineage_events(events: tuple[RunEvent, ...]) -> None:
    """Emit OpenLineage event"""
    adapter = get_openlineage_listener().adapter
    for event in events:
        adapter.emit(event)


def emit_openlineage_events_for_query(
    *,
    query_number: int,
    task_instance: TaskInstance,
    db_type: str,
    query_namespace: str,
    query_id: str | None = None,
    query_text: str | None = None,
    default_database: str | None = None,
    default_schema: str | None = None,
    error: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    is_successful: bool = True,
) -> None:
    """Builds and emits OpenLineage events for a single query execution.

    This function parses the given query text to determine input and output
    datasets, constructs run and job facets, and generates a pair of
    OpenLineage events (start and complete/fail). These events are then emitted
    through the OpenLineage adapter.

    Args:
        query_number: Sequential number of the query within the task.
         Used for creating job_name for OpenLineage events.
        task_instance: The Airflow TaskInstance associated with the query.
        db_type: Database type or dialect (e.g., "postgres", "snowflake").
        query_namespace: Namespace for the query, typically identifying the system or environment.
        query_id: Unique identifier for the query.
        query_text: SQL query text to parse for lineage metadata.
        default_database: Optional default database to use if not specified in the query.
        default_schema: Optional default schema to use if not specified in the query.
        error: Error message if the query execution failed.
        start_time: Exact timestamp when the query execution started.
        end_time: Exact timestamp when the query execution finished.
        is_successful: Whether the query execution was successful.
    """

    inputs: list[Dataset] = []
    outputs: list[Dataset] = []
    if query_text:
        log.debug("Performing sql parsing with provided query text.")
        inputs, outputs = parse_sql(
            query_text=query_text,
            query_dialect=db_type,
            query_namespace=query_namespace,
            default_schema=default_schema,
            default_database=default_database,
        )

    run_facets = create_run_facets(
        query_id=query_id,
        query_namespace=query_namespace,
        error=error,
    )
    parent_run_facet = get_parent_run_facet_with_task_as_parent(task_instance)
    run_facets = {**run_facets, **parent_run_facet}
    job_facets = create_job_facets(
        query_text=query_text,
        integration_name=db_type,
        job_type="QUERY",
    )

    job_name = f"{lineage_job_name(task_instance)}.query.{query_number}"

    log.debug("OpenLineage events for query will be emitted with job name=`%s`", job_name)
    ol_events = create_ol_event_pair(
        job_name=job_name,
        inputs=inputs,
        outputs=outputs,
        run_facets=run_facets,
        job_facets=job_facets,
        start_time=start_time,
        end_time=end_time,
        is_successful=is_successful,
    )

    log.info("Observe SDK will emit %s OpenLineage events.", len(ol_events))
    emit_openlineage_events(ol_events)


def emit_openlineage_running_event(
    *,
    task_instance: TaskInstance,
    inputs: list[Dataset],
    outputs: list[Dataset],
) -> None:
    """Builds and emits OpenLineage event with given input/output datasets.

    This function constructs run and job facets, and generates OpenLineage running event.
    These events are then emitted through the OpenLineage adapter.

    Args:
        inputs: input datasets
        outputs: output datasets
        task_instance: the Airflow TaskInstance.
    """
    parent_run_facet = get_parent_run_facet_with_dag_as_parent(task_instance)
    airflow_run_facet = get_airflow_run_facet(task_instance)
    run_facets = {**parent_run_facet, **airflow_run_facet}

    job_facets = create_job_facets(integration_name="AIRFLOW", job_type="TASK")

    job_name = lineage_job_name(task_instance)
    job_namespace = lineage_job_namespace()
    run_id = lineage_run_id(task_instance)

    ol_event = create_ol_running_event(
        run_id=run_id,
        job_name=job_name,
        job_namespace=job_namespace,
        inputs=inputs,
        outputs=outputs,
        run_facets=run_facets,
        job_facets=job_facets,
    )

    log.info("Observe SDK will emit OpenLineage running event.")
    emit_openlineage_events((ol_event,))
