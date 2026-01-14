import pytest
import datetime
from unittest.mock import patch, MagicMock

from astro_observe_sdk import log_query, log_lineage
from astro_observe_sdk.constants import OPENLINEAGE_PRODUCER
from astro_observe_sdk.lineage import _query_counters
from astro_observe_sdk.utils.database import QueryExecutionContext, QueryExecutionMetadata
from astro_observe_sdk.utils import openlineage
from astro_observe_sdk.utils.openlineage import Dataset


def test_log_query_counter_rises():
    mock_ti = MagicMock(dag_id="dag1", task_id="task1")

    fake_ctx = QueryExecutionContext(
        query_id="q-123",
        query_text="SELECT * FROM table",
        query_job_namespace="databricks://cluster1",
        default_database="db",
        default_schema="sch",
        query_execution_metadata=QueryExecutionMetadata(),
        db_type="databricks",
    )

    with (
        patch("astro_observe_sdk.lineage.get_task_instance_from_context", return_value=mock_ti),
        patch(
            "astro_observe_sdk.lineage.resolve_query_execution_context", return_value=fake_ctx
        ) as mock_resolve,
        patch("astro_observe_sdk.lineage.lineage_run_id", return_value="ti_key") as mock_run_id,
        patch("astro_observe_sdk.lineage.emit_openlineage_events_for_query") as mock_emit,
    ):
        _query_counters.clear()

        log_query(
            query_job_namespace="databricks://cluster1",
            query_text="SELECT * FROM table",
            query_id="q-123",
            default_database="db",
            default_schema="sch",
            task_instance=mock_ti,
        )

        mock_resolve.assert_called_once_with(
            query_id="q-123",
            query_text="SELECT * FROM table",
            query_job_namespace="databricks://cluster1",
            default_database="db",
            default_schema="sch",
            db_connector=None,
            db_connector_extra_args=None,
        )
        mock_run_id.assert_called_once_with(mock_ti)

        mock_emit.assert_called_once_with(
            query_number=1,
            task_instance=mock_ti,
            query_id="q-123",
            query_text="SELECT * FROM table",
            query_namespace="databricks://cluster1",
            db_type="databricks",
            default_database="db",
            default_schema="sch",
            error=None,
            start_time=None,
            end_time=None,
            is_successful=True,
        )

        log_query(
            query_job_namespace="databricks://cluster1",
            query_text="SELECT * FROM table",
            query_id="q-999",
            default_database="db",
            default_schema="sch",
            task_instance=mock_ti,
        )

        mock_emit.assert_called_with(
            query_number=2,  # This increased to 2.
            task_instance=mock_ti,
            query_id="q-123",
            query_text="SELECT * FROM table",
            query_namespace="databricks://cluster1",
            db_type="databricks",
            default_database="db",
            default_schema="sch",
            error=None,
            start_time=None,
            end_time=None,
            is_successful=True,
        )


def test_log_query_emit_ol_args():
    ti = MagicMock(dag_id="d", task_id="t")
    fake_ctx = MagicMock()
    fake_ctx.query_id = "q"
    fake_ctx.query_text = "SELECT X"
    fake_ctx.query_job_namespace = "db://ns"
    fake_ctx.default_database = "db"
    fake_ctx.default_schema = "sch"
    fake_ctx.db_type = "snowflake"
    fake_ctx.query_execution_metadata.error = "ERR123"
    fake_ctx.query_execution_metadata.start_time = datetime.datetime(2024, 1, 1)
    fake_ctx.query_execution_metadata.end_time = datetime.datetime(2024, 1, 2)
    fake_ctx.query_execution_metadata.is_successful = False

    with patch("astro_observe_sdk.lineage.resolve_query_execution_context", return_value=fake_ctx), patch(
        "astro_observe_sdk.lineage.lineage_run_id", return_value="acde070d-8c4c-4f0d-9d8a-162843c10333"
    ), patch("astro_observe_sdk.lineage.emit_openlineage_events_for_query") as mock_emit:
        _query_counters.clear()
        log_query(task_instance=ti)
        kwargs = mock_emit.call_args.kwargs
        assert kwargs["query_number"] == 1
        assert kwargs["task_instance"] == ti
        assert kwargs["query_id"] == "q"
        assert kwargs["query_text"] == "SELECT X"
        assert kwargs["default_database"] == "db"
        assert kwargs["default_schema"] == "sch"
        assert kwargs["query_namespace"] == "db://ns"
        assert kwargs["db_type"] == "snowflake"
        assert kwargs["error"] == "ERR123"
        assert kwargs["start_time"] == datetime.datetime(2024, 1, 1)
        assert kwargs["end_time"] == datetime.datetime(2024, 1, 2)
        assert kwargs["is_successful"] is False


def test_log_query_all_provided_no_external_calls():
    task_uuid = "acde070d-8c4c-4f0d-9d8a-162843c10333"
    query_event_uuid = "acde070d-8c4c-2f0d-9d8a-162843c10333"
    run = openlineage.Run(
        runId="acde070d-8c4c-2f0d-9d8a-162843c10333",
        facets={
            "parent": openlineage.parent_run.ParentRunFacet(
                run=openlineage.parent_run.Run(runId=task_uuid),
                job=openlineage.parent_run.Job(namespace="default", name="d.t"),
                producer=OPENLINEAGE_PRODUCER,
            ),
            "externalQuery": openlineage.external_query_run.ExternalQueryRunFacet(
                externalQueryId="qid",
                source="snowflake://ns",
                producer=OPENLINEAGE_PRODUCER,
            ),
        },
    )
    job = openlineage.Job(
        namespace="default",
        name="d.t.query.1",
        facets={
            "jobType": openlineage.job_type_job.JobTypeJobFacet(
                jobType="QUERY",
                integration="SNOWFLAKE",
                processingType="BATCH",
                producer=OPENLINEAGE_PRODUCER,
            ),
            "sql": openlineage.sql_job.SQLJobFacet(
                query="INSERT INTO a SELECT x, y FROM b;", producer=OPENLINEAGE_PRODUCER
            ),
        },
    )

    fixed_now = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)

    common_kwargs = {
        "run": run,
        "job": job,
        "inputs": [openlineage.Dataset(namespace="snowflake://ns", name="db.sch.b", facets={})],
        "outputs": [openlineage.Dataset(namespace="snowflake://ns", name="db.sch.a", facets={})],
        "eventTime": fixed_now.isoformat(),
        "producer": OPENLINEAGE_PRODUCER,
    }
    start = openlineage.RunEvent(eventType=openlineage.RunState.START, **common_kwargs)
    end = openlineage.RunEvent(eventType=openlineage.RunState.COMPLETE, **common_kwargs)

    with patch.object(openlineage, "emit_openlineage_events") as mock_emit, patch(
        "astro_observe_sdk.lineage.lineage_run_id", return_value=task_uuid
    ), patch.object(openlineage, "lineage_run_id", return_value=task_uuid), patch.object(
        openlineage, "generate_new_uuid", return_value=query_event_uuid
    ), patch("astro_observe_sdk.utils.openlineage.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        _query_counters.clear()

        log_query(
            query_id="qid",
            query_text="INSERT INTO a SELECT x, y FROM b;",
            query_job_namespace="snowflake://ns",
            default_database="db",
            default_schema="sch",
            task_instance=MagicMock(dag_id="d", task_id="t"),
        )
        mock_emit.assert_called_once_with((start, end))


def test_log_query_query_id_and_text_missing_raises():
    with pytest.raises(ValueError, match="At least one of"):
        log_query(query_id=None, query_text=None, query_job_namespace="db://ns", task_instance=MagicMock())


def test_log_query_namespace_missing_not_retrieved_raises():
    with pytest.raises(ValueError, match="`query_job_namespace` is required."):
        log_query(query_text="SELECT 1", db_connector=MagicMock(), task_instance=MagicMock())


def test_log_query_ti_missing_is_retrieved():
    mock_ti = MagicMock(dag_id="dag1", task_id="task1")
    with (
        patch("astro_observe_sdk.lineage.get_task_instance_from_context", return_value=mock_ti),
        patch("astro_observe_sdk.lineage.resolve_query_execution_context", return_value=MagicMock()),
        patch("astro_observe_sdk.lineage.lineage_run_id", return_value="ti_key"),
        patch("astro_observe_sdk.lineage.emit_openlineage_events_for_query") as mock_emit,
    ):
        log_query(query_text="SELECT 1", db_connector=MagicMock(), task_instance=None)

    assert mock_emit.call_args.kwargs["task_instance"] == mock_ti


def test_log_lineage_with_inputs_and_outputs():
    """Test that log_lineage emits RUNNING event with inputs and outputs."""
    mock_ti = MagicMock(dag_id="dag1", task_id="task1")
    input_dataset = Dataset(namespace="snowflake://acc", name="db.sch.input_table", facets={})
    output_dataset = Dataset(namespace="snowflake://acc", name="db.sch.output_table", facets={})

    with patch("astro_observe_sdk.lineage.emit_openlineage_running_event") as mock_emit:
        log_lineage(
            inputs=[input_dataset],
            outputs=[output_dataset],
            task_instance=mock_ti,
        )

        mock_emit.assert_called_once_with(
            task_instance=mock_ti,
            inputs=[input_dataset],
            outputs=[output_dataset],
        )


def test_log_lineage_with_only_inputs():
    """Test that log_lineage works with only inputs provided."""
    mock_ti = MagicMock(dag_id="dag1", task_id="task1")
    input_dataset = Dataset(namespace="databricks://cluster", name="db.sch.input", facets={})

    with patch("astro_observe_sdk.lineage.emit_openlineage_running_event") as mock_emit:
        log_lineage(
            inputs=[input_dataset],
            task_instance=mock_ti,
        )

        mock_emit.assert_called_once_with(
            task_instance=mock_ti,
            inputs=[input_dataset],
            outputs=[],
        )


def test_log_lineage_with_only_outputs():
    """Test that log_lineage works with only outputs provided."""
    mock_ti = MagicMock(dag_id="dag1", task_id="task1")
    output_dataset = Dataset(namespace="bigquery", name="project.dataset.output", facets={})

    with patch("astro_observe_sdk.lineage.emit_openlineage_running_event") as mock_emit:
        log_lineage(
            outputs=[output_dataset],
            task_instance=mock_ti,
        )

        mock_emit.assert_called_once_with(
            task_instance=mock_ti,
            inputs=[],
            outputs=[output_dataset],
        )


def test_log_lineage_ti_missing_is_retrieved():
    """Test that log_lineage retrieves task_instance from context if not provided."""
    mock_ti = MagicMock(dag_id="dag1", task_id="task1")
    input_dataset = Dataset(namespace="snowflake://acc", name="db.sch.table", facets={})

    with (
        patch("astro_observe_sdk.lineage.get_task_instance_from_context", return_value=mock_ti),
        patch("astro_observe_sdk.lineage.emit_openlineage_running_event") as mock_emit,
    ):
        log_lineage(inputs=[input_dataset], task_instance=None)

        mock_emit.assert_called_once_with(
            task_instance=mock_ti,
            inputs=[input_dataset],
            outputs=[],
        )


def test_log_lineage_raises_when_no_inputs_or_outputs():
    """Test that log_lineage raises ValueError when both inputs and outputs are empty."""
    with pytest.raises(ValueError, match="Either `inputs` or `outputs` must be provided"):
        log_lineage(inputs=None, outputs=None, task_instance=MagicMock())


def test_log_lineage_raises_when_empty_lists():
    """Test that log_lineage raises ValueError when both inputs and outputs are empty lists."""
    with pytest.raises(ValueError, match="Either `inputs` or `outputs` must be provided"):
        log_lineage(inputs=[], outputs=[], task_instance=MagicMock())


def test_log_lineage_raises_when_non_dataset_in_inputs():
    """Test that log_lineage raises TypeError when inputs contain non-Dataset objects."""
    mock_ti = MagicMock(dag_id="dag1", task_id="task1")
    with pytest.raises(TypeError, match="Only OpenLineage Datasets are accepted"):
        log_lineage(inputs=["not a dataset"], task_instance=mock_ti)


def test_log_lineage_raises_when_non_dataset_in_outputs():
    """Test that log_lineage raises TypeError when outputs contain non-Dataset objects."""
    mock_ti = MagicMock(dag_id="dag1", task_id="task1")
    with pytest.raises(TypeError, match="Only OpenLineage Datasets are accepted"):
        log_lineage(outputs=[{"not": "a dataset"}], task_instance=mock_ti)


def test_log_lineage_raises_when_mixed_types():
    """Test that log_lineage raises TypeError when inputs/outputs contain mixed types."""
    mock_ti = MagicMock(dag_id="dag1", task_id="task1")
    valid_dataset = Dataset(namespace="snowflake://acc", name="db.sch.table", facets={})

    with pytest.raises(TypeError, match="Only OpenLineage Datasets are accepted"):
        log_lineage(inputs=[valid_dataset, "invalid"], task_instance=mock_ti)
