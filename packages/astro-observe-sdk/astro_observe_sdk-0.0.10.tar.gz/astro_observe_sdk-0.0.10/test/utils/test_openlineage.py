import pytest
import datetime
from unittest.mock import patch, MagicMock

from astro_observe_sdk.constants import OPENLINEAGE_PRODUCER
from astro_observe_sdk.utils.openlineage import (
    parse_sql,
    _parse_sql_default_parser,
    get_parent_run_facet_with_task_as_parent,
    get_parent_run_facet_with_dag_as_parent,
    get_airflow_run_facet,
    create_ol_event_pair,
    create_ol_running_event,
    create_run_facets,
    create_job_facets,
    emit_openlineage_events,
    emit_openlineage_events_for_query,
    emit_openlineage_running_event,
    is_openlineage_enabled,
)

from openlineage.client.facet_v2 import (
    parent_run,
    external_query_run,
    job_type_job,
    sql_job,
    error_message_run,
)


@patch("airflow.providers.openlineage.plugins.listener.get_openlineage_listener")
@patch("airflow.providers.openlineage.conf.is_disabled")
def test_is_openlineage_enabled(mock_is_disabled, mock_get_listener):
    mock_is_disabled.return_value = False
    mock_get_listener.return_value = True
    assert is_openlineage_enabled() is True


@patch("airflow.providers.openlineage.plugins.listener.get_openlineage_listener")
@patch("airflow.providers.openlineage.conf.is_disabled")
def test_is_openlineage_enabled_explicit_disablement(mock_is_disabled, mock_get_listener):
    mock_is_disabled.return_value = True
    assert is_openlineage_enabled() is False


@patch("airflow.providers.openlineage.plugins.listener.get_openlineage_listener")
@patch("airflow.providers.openlineage.conf.is_disabled")
def test_is_openlineage_listener_not_found(mock_is_disabled, mock_get_listener):
    mock_is_disabled.return_value = False
    mock_get_listener.return_value = None
    assert is_openlineage_enabled() is False


@patch("airflow.providers.openlineage.conf.is_disabled")
def test_is_openlineage_enabled_import_error(mock_is_disabled):
    """Test that ImportError is handled when OpenLineage modules cannot be imported."""
    mock_is_disabled.side_effect = RuntimeError("Should not be called.")
    with patch.dict(
        "sys.modules",
        {
            "airflow.providers.openlineage.conf": None,
            "airflow.providers.openlineage.plugins.listener": None,
        },
    ):
        result = is_openlineage_enabled()
        assert result is False


def test_parse_sql_calls_default_parser():
    """Test that parse_sql delegates to _parse_sql_default_parser when type is 'default'."""
    with patch("astro_observe_sdk.utils.openlineage._parse_sql_default_parser") as mock_default_parser:
        mock_default_parser.return_value = (["input"], ["output"])
        result = parse_sql(query_text="SELECT * FROM t", query_namespace="namespace")
        assert result == (["input"], ["output"])
        mock_default_parser.assert_called_once_with(
            query_text="SELECT * FROM t",
            query_namespace="namespace",
            default_schema=None,
            default_database=None,
            query_dialect="generic",
        )


def test_parse_sql_raises_for_non_default():
    """Test that parse_sql raises for unsupported parser types."""
    with pytest.raises(NotImplementedError):
        parse_sql("SELECT 1", "namespace", sql_parser_type="something-else")


def test_parse_sql_default_parser_no_results():
    """Test that _parse_sql_default_parser returns empty lists if parse result is falsy."""
    with patch("astro_observe_sdk.utils.openlineage.SQLParser") as mock_sqlparser:
        mock_instance = mock_sqlparser.return_value
        mock_instance.split_sql_string.return_value = ["split"]
        mock_instance.parse.return_value = None  # No result

        result = _parse_sql_default_parser("SELECT 1", "namespace")
        assert result == ([], [])


def test_parse_sql_default_parser_with_results():
    """Test that _parse_sql_default_parser maps in_tables and out_tables to datasets."""
    mock_parse_result = MagicMock()
    mock_parse_result.in_tables = ["in_table"]
    mock_parse_result.out_tables = ["out_table"]

    with (
        patch("astro_observe_sdk.utils.openlineage.SQLParser") as mock_sqlparser,
        patch("astro_observe_sdk.utils.openlineage.from_table_meta") as mock_from_table_meta,
    ):
        mock_instance = mock_sqlparser.return_value
        mock_instance.split_sql_string.return_value = ["split"]
        mock_instance.parse.return_value = mock_parse_result

        mock_from_table_meta.side_effect = lambda dataset, db, ns, _: f"DS({dataset},{db},{ns})"

        inputs, outputs = _parse_sql_default_parser("SELECT * FROM t", "namespace", default_database="db")

        assert inputs == ["DS(in_table,db,namespace)"]
        assert outputs == ["DS(out_table,db,namespace)"]
        mock_from_table_meta.assert_any_call("in_table", "db", "namespace", False)
        mock_from_table_meta.assert_any_call("out_table", "db", "namespace", False)


def test_parse_sql_default_parser_invalid_dialect_falls_back_to_generic():
    """Test that unsupported dialect falls back to 'generic'."""
    with patch("astro_observe_sdk.utils.openlineage.SQLParser") as mock_sqlparser:
        mock_instance = mock_sqlparser.return_value
        mock_instance.split_sql_string.return_value = ["split"]
        mock_instance.parse.return_value = None

        _parse_sql_default_parser("SELECT 1", "namespace", query_dialect="unsupported")

        mock_sqlparser.assert_called_once_with(dialect="generic", default_schema=None)


def test_get_parent_run_facet_with_task_as_parent_builds_expected_object():
    """Test that get_parent_run_facet_with_task_as_parent constructs ParentRunFacet with lineage values."""
    mock_ti = MagicMock()

    with (
        patch(
            "astro_observe_sdk.utils.openlineage.lineage_run_id",
            return_value="acde070d-8c4c-4f0d-9d8a-162843c10333",
        ) as mock_run_id,
        patch(
            "astro_observe_sdk.utils.openlineage.lineage_job_name", return_value="job-name"
        ) as mock_job_name,
        patch(
            "astro_observe_sdk.utils.openlineage.lineage_job_namespace", return_value="namespace"
        ) as mock_namespace,
    ):
        expected = parent_run.ParentRunFacet(
            run=parent_run.Run(runId="acde070d-8c4c-4f0d-9d8a-162843c10333"),
            job=parent_run.Job(
                namespace="namespace",
                name="job-name",
            ),
            producer=OPENLINEAGE_PRODUCER,
        )
        result = get_parent_run_facet_with_task_as_parent(mock_ti)

        assert result == {"parent": expected}
        mock_run_id.assert_called_once_with(mock_ti)
        mock_job_name.assert_called_once_with(mock_ti)
        mock_namespace.assert_called_once_with()


def test_create_ol_event_pair_defaults_and_success():
    """Test create_ol_event_pair builds start and complete events with defaults."""
    fixed_now = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)

    with (
        patch(
            "astro_observe_sdk.utils.openlineage.generate_new_uuid",
            return_value="acde070d-8c4c-4f0d-9d8a-162843c10333",
        ),
        patch("astro_observe_sdk.utils.openlineage.lineage_job_namespace", return_value="namespace"),
        patch("astro_observe_sdk.utils.openlineage.datetime") as mock_datetime,
    ):
        mock_datetime.now.return_value = fixed_now

        start, end = create_ol_event_pair(job_name="my_job")

        # Verify both events share the same runId
        assert start.run.runId == end.run.runId == "acde070d-8c4c-4f0d-9d8a-162843c10333"
        # Verify job name/namespace
        assert start.job.name == "my_job"
        assert start.job.namespace == "namespace"
        # Verify timestamps
        assert start.eventTime == fixed_now.isoformat()
        assert end.eventTime == fixed_now.isoformat()
        # Verify event types
        assert start.eventType.value == "START"
        assert end.eventType.value == "COMPLETE"


def test_create_ol_event_pair_with_inputs_outputs_and_failure():
    """Test create_ol_event_pair handles inputs, outputs, custom times, and failure state."""
    start_time = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)
    end_time = datetime.datetime(2024, 1, 1, 11, 0, 0, tzinfo=datetime.timezone.utc)

    fake_inputs = ["in1", "in2"]
    fake_outputs = ["out1"]
    fake_run_facets = {"k": "v"}
    fake_job_facets = {"j": "f"}

    with (
        patch(
            "astro_observe_sdk.utils.openlineage.generate_new_uuid",
            return_value="acde070d-8c4c-4f0d-9d8a-162843c10333",
        ),
        patch("astro_observe_sdk.utils.openlineage.lineage_job_namespace", return_value="ns"),
    ):
        start, end = create_ol_event_pair(
            job_name="failing_job",
            start_time=start_time,
            end_time=end_time,
            is_successful=False,
            inputs=fake_inputs,
            outputs=fake_outputs,
            run_facets=fake_run_facets,
            job_facets=fake_job_facets,
        )

        # Verify inputs/outputs passed through
        assert start.inputs == fake_inputs
        assert end.outputs == fake_outputs
        # Verify facets applied
        assert start.run.facets == fake_run_facets
        assert start.job.facets == fake_job_facets
        # Verify failure state
        assert end.eventType.value == "FAIL"
        # Verify timestamps
        assert start.eventTime == start_time.isoformat()
        assert end.eventTime == end_time.isoformat()


def test_create_run_facets_full():
    """Test that create_run_facets includes externalQuery and errorMessage facets."""
    result = create_run_facets(query_id="qid123", query_namespace="ns1", error="err_msg")

    assert result == {
        "externalQuery": external_query_run.ExternalQueryRunFacet(
            externalQueryId="qid123", source="ns1", producer=OPENLINEAGE_PRODUCER
        ),
        "errorMessage": error_message_run.ErrorMessageRunFacet(
            message="err_msg", programmingLanguage="SQL", producer=OPENLINEAGE_PRODUCER
        ),
    }


def test_create_run_facets_without_query_id():
    """Test that create_run_facets only includes errorMessage facet if query_id is missing."""
    result = create_run_facets(query_id=None, query_namespace="ns1", error="err_msg")

    assert result == {
        "errorMessage": error_message_run.ErrorMessageRunFacet(
            message="err_msg", programmingLanguage="SQL", producer=OPENLINEAGE_PRODUCER
        ),
    }


def test_create_run_facets_without_error():
    """Test that create_run_facets only includes externalQuery facet if error is missing."""
    result = create_run_facets(query_id="qid123", query_namespace="ns1", error=None)

    assert result == {
        "externalQuery": external_query_run.ExternalQueryRunFacet(
            externalQueryId="qid123", source="ns1", producer=OPENLINEAGE_PRODUCER
        ),
    }


def test_create_run_facets_empty():
    """Test that create_run_facets returns empty dict when both query_id and error are missing."""
    result = create_run_facets(query_id=None, query_namespace="ns1", error=None)

    assert result == {}


def test_create_job_facets_with_query_text():
    """Test that create_job_facets includes jobType and sql facets."""
    result = create_job_facets(
        integration_name="integrationX", job_type="QUERY", query_text="SELECT * FROM t"
    )

    assert result == {
        "jobType": job_type_job.JobTypeJobFacet(
            jobType="QUERY",
            integration="INTEGRATIONX",
            processingType="BATCH",
            producer=OPENLINEAGE_PRODUCER,
        ),
        "sql": sql_job.SQLJobFacet(query="SELECT * FROM t", producer=OPENLINEAGE_PRODUCER),
    }


def test_create_job_facets_without_query_text():
    """Test that create_job_facets only includes jobType facet when query_text is None."""
    result = create_job_facets(integration_name="integrationY", job_type="TASK", query_text=None)

    assert result == {
        "jobType": job_type_job.JobTypeJobFacet(
            jobType="TASK",
            integration="INTEGRATIONY",
            processingType="BATCH",
            producer=OPENLINEAGE_PRODUCER,
        ),
    }


def test_emit_openlineage_events_emits_each_event():
    """Test that emit_openlineage_events calls adapter.emit for each event."""
    fake_events = ["event1", "event2"]
    mock_adapter = MagicMock()
    mock_listener = MagicMock(adapter=mock_adapter)

    with patch(
        "astro_observe_sdk.utils.openlineage.get_openlineage_listener", return_value=mock_listener
    ) as mock_listener_fn:
        emit_openlineage_events(fake_events)

        mock_listener_fn.assert_called_once_with()
        mock_adapter.emit.assert_any_call("event1")
        mock_adapter.emit.assert_any_call("event2")
        assert mock_adapter.emit.call_count == 2


def test_emit_openlineage_events_for_query_with_query_text():
    ti = MagicMock(dag_id="dag", task_id="task")

    with patch(
        "astro_observe_sdk.utils.openlineage.parse_sql", return_value=(["in"], ["out"])
    ) as mock_parse, patch(
        "astro_observe_sdk.utils.openlineage.create_run_facets", return_value={"rf": "v"}
    ) as mock_run, patch(
        "astro_observe_sdk.utils.openlineage.get_parent_run_facet_with_task_as_parent",
        return_value={"parent": "parent_facet"},
    ) as mock_parent, patch(
        "astro_observe_sdk.utils.openlineage.create_job_facets", return_value={"jf": "v"}
    ) as mock_job, patch(
        "astro_observe_sdk.utils.openlineage.create_ol_event_pair", return_value=("ev1", "ev2")
    ) as mock_pair, patch("astro_observe_sdk.utils.openlineage.emit_openlineage_events") as mock_emit:
        emit_openlineage_events_for_query(
            query_number=1,
            task_instance=ti,
            db_type="snowflake",
            query_namespace="snowflake://acc",
            query_id="qid-1",
            query_text="SELECT * FROM t",
            default_database="db",
            default_schema="sch",
            error="boom",
            start_time=datetime.datetime(2024, 1, 1),
            end_time=datetime.datetime(2024, 1, 2),
            is_successful=False,
        )

        mock_parse.assert_called_once_with(
            query_text="SELECT * FROM t",
            query_dialect="snowflake",
            query_namespace="snowflake://acc",
            default_schema="sch",
            default_database="db",
        )
        mock_run.assert_called_once_with(
            query_id="qid-1",
            query_namespace="snowflake://acc",
            error="boom",
        )
        mock_parent.assert_called_once_with(ti)
        mock_job.assert_called_once_with(
            query_text="SELECT * FROM t",
            integration_name="snowflake",
            job_type="QUERY",
        )
        mock_pair.assert_called_once_with(
            job_name="dag.task.query.1",
            inputs=["in"],
            outputs=["out"],
            run_facets={"rf": "v", "parent": "parent_facet"},
            job_facets={"jf": "v"},
            start_time=datetime.datetime(2024, 1, 1),
            end_time=datetime.datetime(2024, 1, 2),
            is_successful=False,
        )
        mock_emit.assert_called_once_with(("ev1", "ev2"))


def test_emit_openlineage_events_for_query_without_query_text_skips_parse():
    ti = MagicMock(dag_id="dag", task_id="task")

    with patch("astro_observe_sdk.utils.openlineage.parse_sql") as mock_parse, patch(
        "astro_observe_sdk.utils.openlineage.create_run_facets", return_value={}
    ) as mock_run, patch(
        "astro_observe_sdk.utils.openlineage.get_parent_run_facet_with_task_as_parent",
        return_value={"parent": "parent_facet"},
    ) as mock_parent, patch(
        "astro_observe_sdk.utils.openlineage.create_job_facets", return_value={}
    ) as mock_job, patch(
        "astro_observe_sdk.utils.openlineage.create_ol_event_pair", return_value=("ev",)
    ) as mock_pair, patch("astro_observe_sdk.utils.openlineage.emit_openlineage_events") as mock_emit:
        emit_openlineage_events_for_query(
            query_number=99,
            task_instance=ti,
            db_type="databricks",
            query_namespace="db://cluster",
            query_id=None,
            query_text=None,
            default_database=None,
            default_schema=None,
        )

        mock_parse.assert_not_called()
        mock_run.assert_called_once()
        mock_job.assert_called_once_with(query_text=None, integration_name="databricks", job_type="QUERY")
        mock_pair.assert_called_once()
        mock_parent.assert_called_once()
        mock_emit.assert_called_once()


def test_get_parent_run_facet_with_dag_as_parent_airflow_v3_plus():
    """Test that get_parent_run_facet_with_dag_as_parent constructs ParentRunFacet for DAG as parent (Airflow 3.0+)."""
    mock_ti = MagicMock(dag_id="test_dag")
    mock_dagrun = MagicMock()
    mock_dagrun.logical_date = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
    mock_dagrun.run_after = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
    mock_dagrun.clear_number = 5
    mock_ti.get_template_context.return_value = {"dag_run": mock_dagrun}

    with (
        patch("astro_observe_sdk.utils.openlineage.AIRFLOW_V_3_0_PLUS", True),
        patch("airflow.providers.openlineage.plugins.adapter.OpenLineageAdapter") as mock_adapter_class,
        patch(
            "astro_observe_sdk.utils.openlineage.lineage_job_namespace", return_value="namespace"
        ) as mock_namespace,
    ):
        mock_adapter_class.build_dag_run_id.return_value = "acde070d-8c4c-4f0d-9d8a-162843c10333"
        result = get_parent_run_facet_with_dag_as_parent(mock_ti)

        expected = parent_run.ParentRunFacet(
            run=parent_run.Run(runId="acde070d-8c4c-4f0d-9d8a-162843c10333"),
            job=parent_run.Job(namespace="namespace", name="test_dag"),
            producer=OPENLINEAGE_PRODUCER,
        )
        assert result == {"parent": expected}
        mock_adapter_class.build_dag_run_id.assert_called_once_with(
            dag_id="test_dag",
            logical_date=mock_dagrun.logical_date,
            clear_number=5,
        )
        mock_namespace.assert_called_once_with()


def test_get_parent_run_facet_with_dag_as_parent_airflow_v3_plus_no_logical_date():
    """Test that get_parent_run_facet_with_dag_as_parent uses run_after when logical_date is None (Airflow 3.0+)."""
    mock_ti = MagicMock(dag_id="test_dag")
    mock_dagrun = MagicMock()
    mock_dagrun.logical_date = None
    mock_dagrun.run_after = datetime.datetime(2024, 1, 2, tzinfo=datetime.timezone.utc)
    mock_dagrun.clear_number = 0
    mock_ti.get_template_context.return_value = {"dag_run": mock_dagrun}

    with (
        patch("astro_observe_sdk.utils.openlineage.AIRFLOW_V_3_0_PLUS", True),
        patch("airflow.providers.openlineage.plugins.adapter.OpenLineageAdapter") as mock_adapter_class,
        patch(
            "astro_observe_sdk.utils.openlineage.lineage_job_namespace", return_value="namespace"
        ) as mock_namespace,
    ):
        mock_adapter_class.build_dag_run_id.return_value = "acde070d-8c4c-4f0d-9d8a-162843c10333"
        result = get_parent_run_facet_with_dag_as_parent(mock_ti)

        expected = parent_run.ParentRunFacet(
            run=parent_run.Run(runId="acde070d-8c4c-4f0d-9d8a-162843c10333"),
            job=parent_run.Job(namespace="namespace", name="test_dag"),
            producer=OPENLINEAGE_PRODUCER,
        )
        assert result == {"parent": expected}
        mock_adapter_class.build_dag_run_id.assert_called_once_with(
            dag_id="test_dag",
            logical_date=mock_dagrun.run_after,
            clear_number=0,
        )
        mock_namespace.assert_called_once_with()


def test_get_parent_run_facet_with_dag_as_parent_airflow_v2():
    """Test that get_parent_run_facet_with_dag_as_parent constructs ParentRunFacet for DAG as parent (Airflow 2.x)."""
    mock_ti = MagicMock(dag_id="test_dag")
    mock_dagrun = MagicMock()
    mock_dagrun.logical_date = datetime.datetime(2024, 2, 1, tzinfo=datetime.timezone.utc)
    mock_dagrun.execution_date = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
    delattr(mock_dagrun, "clear_number")
    mock_ti.dag_run = mock_dagrun

    with (
        patch("astro_observe_sdk.utils.openlineage.AIRFLOW_V_3_0_PLUS", False),
        patch("airflow.providers.openlineage.plugins.adapter.OpenLineageAdapter") as mock_adapter_class,
        patch(
            "astro_observe_sdk.utils.openlineage.lineage_job_namespace", return_value="namespace"
        ) as mock_namespace,
    ):
        mock_adapter_class.build_dag_run_id.return_value = "acde070d-8c4c-4f0d-9d8a-162843c10333"
        result = get_parent_run_facet_with_dag_as_parent(mock_ti)

        expected = parent_run.ParentRunFacet(
            run=parent_run.Run(runId="acde070d-8c4c-4f0d-9d8a-162843c10333"),
            job=parent_run.Job(namespace="namespace", name="test_dag"),
            producer=OPENLINEAGE_PRODUCER,
        )
        assert result == {"parent": expected}
        mock_adapter_class.build_dag_run_id.assert_called_once_with(
            dag_id="test_dag",
            logical_date=mock_dagrun.logical_date,
            clear_number=0,
        )
        mock_namespace.assert_called_once_with()


def test_get_parent_run_facet_with_dag_as_parent_fallback_to_logical_date():
    """Test that get_parent_run_facet_with_dag_as_parent falls back to logical_date only if clear_number fails."""
    mock_ti = MagicMock(dag_id="test_dag")
    mock_dagrun = MagicMock()
    mock_dagrun.logical_date = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
    mock_ti.get_template_context.return_value = {"dag_run": mock_dagrun}

    with (
        patch("astro_observe_sdk.utils.openlineage.AIRFLOW_V_3_0_PLUS", True),
        patch("airflow.providers.openlineage.plugins.adapter.OpenLineageAdapter") as mock_adapter_class,
        patch("astro_observe_sdk.utils.openlineage.lineage_job_namespace", return_value="namespace"),
    ):
        # First call raises TypeError, second succeeds
        mock_adapter_class.build_dag_run_id.side_effect = [
            TypeError("clear_number not supported"),
            "acde070d-8c4c-4f0d-9d8a-162843c10333",
        ]
        result = get_parent_run_facet_with_dag_as_parent(mock_ti)

        expected = parent_run.ParentRunFacet(
            run=parent_run.Run(runId="acde070d-8c4c-4f0d-9d8a-162843c10333"),
            job=parent_run.Job(namespace="namespace", name="test_dag"),
            producer=OPENLINEAGE_PRODUCER,
        )
        assert result == {"parent": expected}
        assert mock_adapter_class.build_dag_run_id.call_count == 2


def test_get_parent_run_facet_with_dag_as_parent_fallback_to_execution_date():
    """Test that get_parent_run_facet_with_dag_as_parent falls back to execution_date if both other attempts fail."""
    mock_ti = MagicMock(dag_id="test_dag")
    mock_dagrun = MagicMock()
    mock_dagrun.logical_date = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
    mock_dagrun.execution_date = datetime.datetime(2024, 1, 2, tzinfo=datetime.timezone.utc)
    mock_ti.get_template_context.return_value = {"dag_run": mock_dagrun}

    with (
        patch("astro_observe_sdk.utils.openlineage.AIRFLOW_V_3_0_PLUS", True),
        patch("airflow.providers.openlineage.plugins.adapter.OpenLineageAdapter") as mock_adapter_class,
        patch("astro_observe_sdk.utils.openlineage.lineage_job_namespace", return_value="namespace"),
    ):
        # First two calls raise TypeError, third succeeds
        mock_adapter_class.build_dag_run_id.side_effect = [
            TypeError("clear_number not supported"),
            TypeError("logical_date not supported"),
            "acde070d-8c4c-4f0d-9d8a-162843c10333",
        ]
        result = get_parent_run_facet_with_dag_as_parent(mock_ti)

        expected = parent_run.ParentRunFacet(
            run=parent_run.Run(runId="acde070d-8c4c-4f0d-9d8a-162843c10333"),
            job=parent_run.Job(namespace="namespace", name="test_dag"),
            producer=OPENLINEAGE_PRODUCER,
        )
        assert result == {"parent": expected}
        assert mock_adapter_class.build_dag_run_id.call_count == 3


def test_get_airflow_run_facet_airflow_v3_plus():
    """Test that get_airflow_run_facet works with Airflow 3.0+."""
    mock_ti = MagicMock()
    mock_context = {
        "task": MagicMock(),
        "dag_run": MagicMock(),
        "dag": MagicMock(),
    }
    mock_ti.get_template_context.return_value = mock_context

    with (
        patch("astro_observe_sdk.utils.openlineage.AIRFLOW_V_3_0_PLUS", True),
        patch("airflow.providers.openlineage.utils.utils.get_airflow_run_facet") as mock_get_facet,
        patch(
            "astro_observe_sdk.utils.openlineage.lineage_run_id",
            return_value="acde070d-8c4c-4f0d-9d8a-162843c10333",
        ) as mock_run_id,
    ):
        mock_get_facet.return_value = {"airflow": "facet"}
        result = get_airflow_run_facet(mock_ti)

        assert result == {"airflow": "facet"}
        mock_get_facet.assert_called_once_with(
            dag_run=mock_context["dag_run"],
            dag=mock_context["dag"],
            task_instance=mock_ti,
            task=mock_context["task"],
            task_uuid="acde070d-8c4c-4f0d-9d8a-162843c10333",
        )
        mock_run_id.assert_called_once_with(mock_ti)


def test_get_airflow_run_facet_airflow_v2():
    """Test that get_airflow_run_facet works with Airflow 2.x."""
    mock_ti = MagicMock(dag_run=MagicMock())
    mock_task = MagicMock()
    mock_dag = MagicMock()
    mock_task.dag = mock_dag
    mock_ti.task = mock_task

    with (
        patch("astro_observe_sdk.utils.openlineage.AIRFLOW_V_3_0_PLUS", False),
        patch("airflow.providers.openlineage.utils.utils.get_airflow_run_facet") as mock_get_facet,
        patch(
            "astro_observe_sdk.utils.openlineage.lineage_run_id",
            return_value="acde070d-8c4c-4f0d-9d8a-162843c10333",
        ) as mock_run_id,
    ):
        mock_get_facet.return_value = {"airflow": "facet_v2"}
        result = get_airflow_run_facet(mock_ti)

        assert result == {"airflow": "facet_v2"}
        mock_get_facet.assert_called_once_with(
            dag_run=mock_ti.dag_run,
            dag=mock_dag,
            task_instance=mock_ti,
            task=mock_task,
            task_uuid="acde070d-8c4c-4f0d-9d8a-162843c10333",
        )
        mock_run_id.assert_called_once_with(mock_ti)


def test_create_ol_running_event():
    """Test that create_ol_running_event creates a RUNNING event with correct structure."""
    fixed_now = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    fake_inputs = ["in1", "in2"]
    fake_outputs = ["out1"]
    fake_run_facets = {"run": "facet"}
    fake_job_facets = {"job": "facet"}

    with patch("astro_observe_sdk.utils.openlineage.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now

        result = create_ol_running_event(
            run_id="acde070d-8c4c-4f0d-9d8a-162843c10333",
            job_name="test_job",
            job_namespace="test_namespace",
            inputs=fake_inputs,
            outputs=fake_outputs,
            run_facets=fake_run_facets,
            job_facets=fake_job_facets,
        )

        assert result.eventType.value == "RUNNING"
        assert result.eventTime == fixed_now.isoformat()
        assert result.run.runId == "acde070d-8c4c-4f0d-9d8a-162843c10333"
        assert result.run.facets == fake_run_facets
        assert result.job.name == "test_job"
        assert result.job.namespace == "test_namespace"
        assert result.job.facets == fake_job_facets
        assert result.inputs == fake_inputs
        assert result.outputs == fake_outputs
        assert result.producer == OPENLINEAGE_PRODUCER


def test_create_ol_running_event_defaults():
    """Test that create_ol_running_event handles None inputs/outputs/facets."""
    fixed_now = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)

    with patch("astro_observe_sdk.utils.openlineage.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now

        result = create_ol_running_event(
            run_id="acde070d-8c4c-4f0d-9d8a-162843c10333",
            job_name="test_job2",
            job_namespace="test_namespace2",
        )

        assert result.eventType.value == "RUNNING"
        assert result.run.runId == "acde070d-8c4c-4f0d-9d8a-162843c10333"
        assert result.run.facets == {}
        assert result.job.name == "test_job2"
        assert result.job.namespace == "test_namespace2"
        assert result.job.facets == {}
        assert result.inputs == []
        assert result.outputs == []


def test_emit_openlineage_running_event():
    """Test that emit_openlineage_running_event builds and emits RUNNING event."""
    mock_ti = MagicMock(name="TaskInstance")
    mock_ti.dag_id = "test_dag"
    fake_inputs = [MagicMock()]
    fake_outputs = [MagicMock()]

    with (
        patch(
            "astro_observe_sdk.utils.openlineage.get_parent_run_facet_with_dag_as_parent",
            return_value={"parent": "facet"},
        ) as mock_parent,
        patch(
            "astro_observe_sdk.utils.openlineage.get_airflow_run_facet",
            return_value={"airflow": "facet"},
        ) as mock_airflow,
        patch(
            "astro_observe_sdk.utils.openlineage.create_job_facets",
            return_value={"job": "facet"},
        ) as mock_job_facets,
        patch(
            "astro_observe_sdk.utils.openlineage.lineage_job_name", return_value="test_job"
        ) as mock_job_name,
        patch(
            "astro_observe_sdk.utils.openlineage.lineage_job_namespace", return_value="namespace"
        ) as mock_namespace,
        patch(
            "astro_observe_sdk.utils.openlineage.lineage_run_id",
            return_value="acde070d-8c4c-4f0d-9d8a-162843c10333",
        ) as mock_run_id,
        patch(
            "astro_observe_sdk.utils.openlineage.create_ol_running_event",
            return_value=MagicMock(),
        ) as mock_create_event,
        patch("astro_observe_sdk.utils.openlineage.emit_openlineage_events") as mock_emit,
    ):
        emit_openlineage_running_event(
            task_instance=mock_ti,
            inputs=fake_inputs,
            outputs=fake_outputs,
        )

        mock_parent.assert_called_once_with(mock_ti)
        mock_airflow.assert_called_once_with(mock_ti)
        mock_job_facets.assert_called_once_with(integration_name="AIRFLOW", job_type="TASK")
        mock_job_name.assert_called_once_with(mock_ti)
        mock_namespace.assert_called_once_with()
        mock_run_id.assert_called_once_with(mock_ti)
        mock_create_event.assert_called_once_with(
            run_id="acde070d-8c4c-4f0d-9d8a-162843c10333",
            job_name="test_job",
            job_namespace="namespace",
            inputs=fake_inputs,
            outputs=fake_outputs,
            run_facets={"parent": "facet", "airflow": "facet"},
            job_facets={"job": "facet"},
        )
        mock_emit.assert_called_once()
