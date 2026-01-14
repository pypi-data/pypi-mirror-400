import datetime
import pytest
from astro_observe_sdk.utils import database
from unittest.mock import MagicMock, patch


SnowflakeCursor = type("SnowflakeCursor", (MagicMock,), {})
Cursor = type("Cursor", (MagicMock,), {})  # Databricks
RandomConnector = type("RandomConnector", (MagicMock,), {})


def test_query_execution_metadata_defaults():
    meta = database.QueryExecutionMetadata()
    assert meta.query_id is None
    assert meta.query_text is None
    assert meta.is_successful is True
    assert meta.start_time is None
    assert meta.end_time is None
    assert meta.error is None


def test_query_execution_metadata_custom_values():
    now = datetime.datetime(2025, 1, 1)
    meta = database.QueryExecutionMetadata(
        query_id="q123",
        query_text="SELECT 1",
        is_successful=False,
        start_time=now,
        end_time=now,
        error="some error",
    )
    assert meta.query_id == "q123"
    assert meta.query_text == "SELECT 1"
    assert meta.is_successful is False
    assert meta.start_time == now
    assert meta.end_time == now
    assert meta.error == "some error"


@pytest.mark.parametrize(
    "connector_cls,expected",
    [
        (SnowflakeCursor, database.SNOWFLAKE_DB_TYPE),
        (Cursor, database.DATABRICKS_DB_TYPE),
        (RandomConnector, None),
    ],
)
def test_dbtype_from_connector(connector_cls, expected):
    connector = connector_cls()
    assert database.db_type_from_connector(connector) == expected


@pytest.mark.parametrize(
    "namespace,expected",
    [
        ("snowflake://org_id-acc_id", database.SNOWFLAKE_DB_TYPE),
        ("databricks://adb-123.10.azuredatabricks.net", database.DATABRICKS_DB_TYPE),
        ("mysql://host/db", "mysql"),
        ("", ""),
    ],
)
def test_dbtype_from_query_job_namespace(namespace, expected):
    assert database.db_type_from_query_job_namespace(namespace) == expected


def test_query_execution_context_full_initialization():
    qm = database.QueryExecutionMetadata(
        query_id="q1",
        query_text="SELECT 1",
        is_successful=True,
        start_time=datetime.datetime(2023, 1, 1),
        end_time=datetime.datetime(2023, 1, 1, 0, 1),
    )
    ctx = database.QueryExecutionContext(
        query_id="q1",
        query_text="SELECT 1",
        query_job_namespace="snowflake://acc",
        default_database="db",
        default_schema="schema",
        query_execution_metadata=qm,
        db_type=database.SNOWFLAKE_DB_TYPE,
    )

    assert ctx.query_id == "q1"
    assert ctx.query_text == "SELECT 1"
    assert ctx.query_job_namespace == "snowflake://acc"
    assert ctx.default_database == "db"
    assert ctx.default_schema == "schema"
    assert ctx.query_execution_metadata == qm
    assert ctx.db_type == database.SNOWFLAKE_DB_TYPE


def test_query_execution_context_allows_none_values():
    qm = database.QueryExecutionMetadata()
    ctx = database.QueryExecutionContext(
        query_id=None,
        query_text=None,
        query_job_namespace="databricks://cluster",
        default_database=None,
        default_schema=None,
        query_execution_metadata=qm,
        db_type=database.DATABRICKS_DB_TYPE,
    )

    assert ctx.query_id is None
    assert ctx.query_text is None
    assert ctx.default_database is None
    assert ctx.default_schema is None
    assert ctx.query_execution_metadata == qm
    assert ctx.db_type == database.DATABRICKS_DB_TYPE


def test_resolve_query_context_gets_query_id_from_connector():
    connector = MagicMock()
    query_id = "qid-123"
    with patch.object(database, "get_query_id", return_value=query_id) as mock_qid, patch.object(
        database, "get_query_job_namespace", return_value="db://ns"
    ), patch.object(database, "db_type_from_query_job_namespace", return_value="other"):
        ctx = database.resolve_query_execution_context(
            query_id=None,
            query_text="SELECT 1",
            db_connector=connector,
            query_job_namespace="db://ns",
            default_database="db",
            default_schema="sch",
            db_connector_extra_args=None,
        )

        mock_qid.assert_called_once_with(db_connector=connector, offline_mode=False)
        assert isinstance(ctx, database.QueryExecutionContext)
        assert ctx.query_id == query_id
        assert ctx.query_text == "SELECT 1"
        assert ctx.query_job_namespace == "db://ns"
        assert ctx.default_database == "db"
        assert ctx.default_schema == "sch"
        assert ctx.query_execution_metadata == database.QueryExecutionMetadata()
        assert ctx.db_type == "other"


def test_resolve_query_context_gets_namespace_from_connector():
    connector = MagicMock()
    with patch.object(database, "get_query_id", return_value="qid"), patch.object(
        database, "get_query_job_namespace", return_value="db://from-conn"
    ) as mock_ns, patch.object(database, "db_type_from_query_job_namespace", return_value="other"):
        ctx = database.resolve_query_execution_context(
            query_id="qid",
            query_text="SELECT 1",
            db_connector=connector,
            query_job_namespace=None,
            default_database="db",
            default_schema="sch",
            db_connector_extra_args={"extra": "yes", "offline_mode": True},
        )

        mock_ns.assert_called_once_with(
            db_connector=connector, db_connector_extra_args={"extra": "yes"}, offline_mode=True
        )
        assert isinstance(ctx, database.QueryExecutionContext)
        assert ctx.query_id == "qid"
        assert ctx.query_text == "SELECT 1"
        assert ctx.query_job_namespace == "db://from-conn"
        assert ctx.default_database == "db"
        assert ctx.default_schema == "sch"
        assert ctx.query_execution_metadata == database.QueryExecutionMetadata()
        assert ctx.db_type == "other"


def test_resolve_query_context_raises_if_no_namespace():
    with patch.object(database, "get_query_job_namespace", return_value=None):
        with pytest.raises(ValueError, match="`query_job_namespace` is required."):
            database.resolve_query_execution_context(
                query_id="qid",
                query_text="SELECT 1",
                db_connector=MagicMock(),
                query_job_namespace=None,
                default_database="db",
                default_schema="sch",
                db_connector_extra_args=None,
            )


def test_resolve_query_context_gets_query_text_from_metadata():
    connector = MagicMock()
    qm = database.QueryExecutionMetadata(query_text="from-meta")
    with patch.object(database, "get_query_id", return_value="qid"), patch.object(
        database, "get_query_job_namespace", return_value="db://ns"
    ), patch.object(database, "get_query_execution_metadata", return_value=qm) as mock_meta, patch.object(
        database, "db_type_from_query_job_namespace", return_value="other"
    ):
        ctx = database.resolve_query_execution_context(
            query_id="qid",
            query_text=None,
            db_connector=connector,
            query_job_namespace=None,
            default_database="db",
            default_schema="sch",
            db_connector_extra_args=None,
        )
        mock_meta.assert_called_once_with(
            db_connector=connector,
            query_id="qid",
            db_connector_extra_args={},
            offline_mode=False,
        )
        assert isinstance(ctx, database.QueryExecutionContext)
        assert ctx.query_id == "qid"
        assert ctx.query_text == "from-meta"
        assert ctx.query_job_namespace == "db://ns"
        assert ctx.default_database == "db"
        assert ctx.default_schema == "sch"
        assert ctx.query_execution_metadata == qm
        assert ctx.db_type == "other"


def test_resolve_query_context_raises_if_both_id_and_text_missing():
    with patch.object(database, "get_query_id", return_value=None), patch.object(
        database, "get_query_job_namespace", return_value="db://ns"
    ), patch.object(
        database,
        "get_query_execution_metadata",
        return_value=database.QueryExecutionMetadata(query_text=None),
    ):
        with pytest.raises(ValueError, match="At least one of"):
            database.resolve_query_execution_context(
                query_id=None,
                query_text=None,
                db_connector=MagicMock(),
                query_job_namespace="db://ns",
                default_database="db",
                default_schema="sch",
                db_connector_extra_args=None,
            )


def test_resolve_query_context_gets_default_schema_if_missing():
    connector = MagicMock()
    qm = database.QueryExecutionMetadata(query_text="SELECT 1")
    with patch.object(database, "get_query_id", return_value="qid"), patch.object(
        database, "get_query_job_namespace", return_value="db://ns"
    ), patch.object(database, "get_query_execution_metadata", return_value=qm), patch.object(
        database, "get_default_db_schema", return_value=("XXX", "ssch")
    ) as mock_def, patch.object(
        database, "db_type_from_query_job_namespace", return_value=database.SNOWFLAKE_DB_TYPE
    ):
        ctx = database.resolve_query_execution_context(
            query_id="qid",
            query_text=None,
            db_connector=connector,
            query_job_namespace=None,
            default_database="ddb",
            default_schema=None,
            db_connector_extra_args=None,
        )
        mock_def.assert_called_once_with(db_connector=connector, offline_mode=False)
        assert ctx.default_database == "ddb"
        assert ctx.default_schema == "ssch"
        assert ctx.db_type == database.SNOWFLAKE_DB_TYPE


def test_resolve_query_context_query_id_missing_and_not_from_connector_but_query_text_present():
    connector = MagicMock()
    qm = database.QueryExecutionMetadata(query_text="text-ok")
    with patch.object(database, "get_query_id", return_value=None), patch.object(
        database, "get_query_job_namespace", return_value="db://ns"
    ), patch.object(database, "get_query_execution_metadata", return_value=qm), patch.object(
        database, "db_type_from_query_job_namespace", return_value=database.DATABRICKS_DB_TYPE
    ):
        ctx = database.resolve_query_execution_context(
            query_id=None,
            query_text="text-ok",
            db_connector=connector,
            query_job_namespace=None,
            default_database="db",
            default_schema="sch",
            db_connector_extra_args=None,
        )
        assert ctx.query_id is None
        assert ctx.query_text == "text-ok"
        assert ctx.query_job_namespace == "db://ns"
        assert ctx.db_type == database.DATABRICKS_DB_TYPE


def test_resolve_query_context_query_text_missing_but_query_id_present():
    connector = MagicMock()
    qm = database.QueryExecutionMetadata(query_text=None)
    with patch.object(database, "get_query_id", return_value="qid-only"), patch.object(
        database, "get_query_job_namespace", return_value="db://ns"
    ), patch.object(database, "get_query_execution_metadata", return_value=qm), patch.object(
        database, "db_type_from_query_job_namespace", return_value=database.SNOWFLAKE_DB_TYPE
    ):
        ctx = database.resolve_query_execution_context(
            query_id="qid-only",
            query_text=None,
            db_connector=connector,
            query_job_namespace=None,
            default_database="db",
            default_schema="sch",
            db_connector_extra_args=None,
        )
        assert ctx.query_id == "qid-only"
        assert ctx.query_text is None
        assert ctx.query_job_namespace == "db://ns"
        assert ctx.db_type == database.SNOWFLAKE_DB_TYPE


def test_resolve_query_context_gets_both_defaults_if_missing():
    connector = MagicMock()
    qm = database.QueryExecutionMetadata(query_text="SELECT 1")
    with patch.object(database, "get_query_id", return_value="qid"), patch.object(
        database, "get_query_job_namespace", return_value="db://ns"
    ), patch.object(database, "get_query_execution_metadata", return_value=qm), patch.object(
        database, "get_default_db_schema", return_value=("ddb", "ssch")
    ) as mock_def, patch.object(
        database, "db_type_from_query_job_namespace", return_value=database.SNOWFLAKE_DB_TYPE
    ):
        ctx = database.resolve_query_execution_context(
            query_id="qid",
            query_text="SELECT 1",
            db_connector=connector,
            query_job_namespace=None,
            default_database=None,
            default_schema=None,
            db_connector_extra_args=None,
        )
        mock_def.assert_called_once_with(db_connector=connector, offline_mode=False)
        assert ctx.default_database == "ddb"
        assert ctx.default_schema == "ssch"
        assert ctx.db_type == database.SNOWFLAKE_DB_TYPE


def test_get_query_id_accepts_offline_mode():
    connector = SnowflakeCursor()
    del connector.query_id
    connector.sfqid = "sfq-789"
    assert database.get_query_id(db_connector=connector, offline_mode=True) == "sfq-789"


def test_get_query_id_snowflake():
    connector = SnowflakeCursor()
    del connector.query_id
    connector.sfqid = "sfq-789"
    assert database.get_query_id(db_connector=connector) == "sfq-789"


def test_get_query_id_snowflake_missing():
    connector = SnowflakeCursor()
    del connector.query_id
    del connector.sfqid
    assert database.get_query_id(db_connector=connector) is None


def test_get_query_id_databricks():
    connector = Cursor()
    connector.query_id = "dbq-999"
    assert database.get_query_id(db_connector=connector) == "dbq-999"


def test_get_query_id_databricks_missing():
    connector = Cursor()
    del connector.query_id
    del connector.sfqid
    assert database.get_query_id(db_connector=connector) is None


def test_get_query_id_unknown():
    connector = RandomConnector()
    del connector.query_id
    del connector.sfqid
    assert database.get_query_id(db_connector=connector) is None


@patch.object(database, "db_type_from_connector", return_value=database.SNOWFLAKE_DB_TYPE)
def test_get_query_job_namespace_snowflake_from_extra_args(mock_from_connector):
    connector = MagicMock()
    ns = database.get_query_job_namespace(connector, {"account_id": "custom-host"})
    assert ns == "snowflake://custom-host"


@patch.object(database, "db_type_from_connector", return_value=database.SNOWFLAKE_DB_TYPE)
def test_get_query_job_namespace_snowflake_from_connection_host(mock_from_connector):
    connector = MagicMock()
    connector.connection.host = "org-acc.snowflakecomputing.com"
    ns = database.get_query_job_namespace(connector, {})
    assert ns == "snowflake://org-acc"


@patch.object(database, "db_type_from_connector", return_value=database.SNOWFLAKE_DB_TYPE)
def test_get_query_job_namespace_snowflake_from_db(mock_from_connector):
    connector = MagicMock()
    connector.connection.host = None
    connector.execute.return_value.fetchone.return_value = ("org-acc",)
    ns = database.get_query_job_namespace(connector, {})
    assert ns == "snowflake://org-acc"


@patch.object(database, "db_type_from_connector", return_value=database.SNOWFLAKE_DB_TYPE)
def test_get_query_job_namespace_snowflake_from_db_in_offline_mode(mock_from_connector):
    connector = MagicMock()
    connector.connection.host = None
    connector.execute.return_value.fetchone.return_value = ("org-acc",)
    ns = database.get_query_job_namespace(
        db_connector=connector, db_connector_extra_args={}, offline_mode=True
    )
    assert ns is None
    connector.execute.assert_not_called()


@patch.object(database, "db_type_from_connector", return_value=database.SNOWFLAKE_DB_TYPE)
def test_get_query_job_namespace_snowflake_namespace_db_missing(mock_from_connector):
    connector = MagicMock()
    connector.connection.host = None
    connector.execute.return_value.fetchone.return_value = None
    ns = database.get_query_job_namespace(connector, {})
    assert ns is None


@patch.object(database, "db_type_from_connector", return_value=database.DATABRICKS_DB_TYPE)
def test_get_query_job_namespace_databricks_from_extra_args(mock_from_connector):
    connector = MagicMock()
    ns = database.get_query_job_namespace(connector, {"host": "db-host"})
    assert ns == "databricks://db-host"


@patch.object(database, "db_type_from_connector", return_value=database.DATABRICKS_DB_TYPE)
def test_get_query_job_namespace_databricks_from_session_host(mock_from_connector):
    connector = MagicMock()
    connector.connection.session.host = "session-host"
    ns = database.get_query_job_namespace(connector, {})
    assert ns == "databricks://session-host"


@patch.object(database, "db_type_from_connector", return_value=database.DATABRICKS_DB_TYPE)
def test_get_query_job_namespace_databricks_from_http_client_config(mock_from_connector):
    connector = MagicMock()
    connector.connection.session.host = None
    connector.connection.http_client.config.hostname = "http-host"
    ns = database.get_query_job_namespace(connector, {})
    assert ns == "databricks://http-host"


@patch.object(database, "db_type_from_connector", return_value=database.DATABRICKS_DB_TYPE)
def test_get_query_job_namespace_databricks_no_host(mock_from_connector):
    connector = MagicMock()
    connector.connection.session.host = None
    connector.connection.http_client.config.hostname = None
    ns = database.get_query_job_namespace(connector, {})
    assert ns is None


@patch("astro_observe_sdk.utils.database.requests.get")
@patch.object(database, "db_type_from_connector", return_value=database.DATABRICKS_DB_TYPE)
def test_get_query_job_namespace_databricks_no_host_offline_mode(mock_from_connector, mock_get):
    connector = MagicMock()
    connector.connection.session.host = None
    connector.connection.http_client.config.hostname = None
    ns = database.get_query_job_namespace(connector, {})
    assert ns is None
    connector.execute.assert_not_called()
    mock_get.assert_not_called()


@patch.object(database, "db_type_from_connector", return_value="unknown://something")
def test_get_query_job_namespace_unknown_connector_returns_none(mock_from_connector):
    connector = MagicMock()
    ns = database.get_query_job_namespace(connector, {})
    assert ns is None


@patch.object(database, "db_type_from_connector", return_value=database.SNOWFLAKE_DB_TYPE)
def test_get_default_db_schema_snowflake_direct_values(mock_from_connector):
    connector = MagicMock()
    connector.connection.database = "MY_DB"
    connector.connection.schema = "MY_SCHEMA"
    result = database.get_default_db_schema(connector)
    assert result == ("MY_DB", "MY_SCHEMA")


@patch.object(database, "db_type_from_connector", return_value=database.SNOWFLAKE_DB_TYPE)
def test_get_default_db_schema_snowflake_fallback_to_db(mock_from_connector):
    connector = MagicMock()
    connector.connection.database = None
    connector.connection.schema = "MY_SCHEMA"
    connector.execute.return_value.fetchone.return_value = ("FALLBACK_DB", "FALLBACK_SCHEMA")
    result = database.get_default_db_schema(connector)
    # db is None, schema provided → fallback fills db only
    assert result == ("FALLBACK_DB", "MY_SCHEMA")


@patch.object(database, "db_type_from_connector", return_value=database.SNOWFLAKE_DB_TYPE)
def test_get_default_db_schema_snowflake_offline_mode(mock_from_connector):
    connector = MagicMock()
    connector.connection.database = None
    connector.connection.schema = "MY_SCHEMA"
    connector.execute.return_value.fetchone.return_value = ("FALLBACK_DB", "FALLBACK_SCHEMA")
    result = database.get_default_db_schema(db_connector=connector, offline_mode=True)
    assert result == (None, "MY_SCHEMA")
    connector.execute.assert_not_called()


@patch.object(database, "db_type_from_connector", return_value=database.SNOWFLAKE_DB_TYPE)
def test_get_default_db_schema_snowflake_none_everywhere(mock_from_connector):
    connector = MagicMock()
    connector.connection.database = None
    connector.connection.schema = None
    connector.execute.return_value.fetchone.return_value = None
    result = database.get_default_db_schema(connector)
    assert result == (None, None)


@patch.object(database, "db_type_from_connector", return_value=database.DATABRICKS_DB_TYPE)
def test_get_default_db_schema_databricks_direct_values(mock_from_connector):
    connector = MagicMock()
    connector.connection.session.catalog = "CATALOG1"
    connector.connection.session.schema = "SCHEMA1"
    result = database.get_default_db_schema(connector)
    assert result == ("CATALOG1", "SCHEMA1")


@patch.object(database, "db_type_from_connector", return_value=database.DATABRICKS_DB_TYPE)
def test_get_default_db_schema_databricks_fallback_to_db(mock_from_connector):
    connector = MagicMock()
    connector.connection.session.catalog = None
    connector.connection.session.schema = "MY_SCHEMA"
    connector.execute.return_value.fetchone.return_value = ("CATALOG2", "SCHEMA2")
    result = database.get_default_db_schema(connector)
    assert result == ("CATALOG2", "MY_SCHEMA")


@patch("astro_observe_sdk.utils.database.requests.get")
@patch.object(database, "db_type_from_connector", return_value=database.DATABRICKS_DB_TYPE)
def test_get_default_db_schema_databricks_offline_mode(mock_from_connector, mock_get):
    connector = MagicMock()
    connector.connection.session.catalog = None
    connector.connection.session.schema = "MY_SCHEMA"
    connector.execute.return_value.fetchone.return_value = ("CATALOG2", "SCHEMA2")
    result = database.get_default_db_schema(db_connector=connector, offline_mode=True)
    assert result == (None, "MY_SCHEMA")
    connector.execute.assert_not_called()
    mock_get.assert_not_called()


@patch.object(database, "db_type_from_connector", return_value=database.DATABRICKS_DB_TYPE)
def test_get_default_db_schema_databricks_none_everywhere(mock_from_connector):
    connector = MagicMock()
    connector.connection.session.catalog = None
    connector.connection.session.schema = None
    connector.execute.return_value.fetchone.return_value = None
    result = database.get_default_db_schema(connector)
    assert result == (None, None)


@patch.object(database, "db_type_from_connector", return_value="other")
def test_get_default_db_schema_unknown_connector(mock_from_connector):
    connector = MagicMock()
    result = database.get_default_db_schema(connector)
    assert result == (None, None)


def _empty_databricks_connection():
    conn = MagicMock()
    conn.session = MagicMock()
    conn.http_client = MagicMock()
    conn.session.host = None
    conn.session.auth_provider = None
    conn.http_client.config = MagicMock()
    conn.http_client.config.hostname = None
    return conn


def test_get_databricks_host_from_extra_args():
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    host = database._get_databricks_host(connector, {"host": "extra-host"})
    assert host == "extra-host"


def test_get_databricks_host_from_session():
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    connector.connection.session.host = "session-host"
    host = database._get_databricks_host(connector, {})
    assert host == "session-host"


def test_get_databricks_host_from_session_offline_mode():
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    connector.connection.session.host = "session-host"
    host = database._get_databricks_host(
        db_connector=connector, db_connector_extra_args={}, offline_mode=True
    )
    assert host == "session-host"


def test_get_databricks_host_from_http_client():
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    connector.connection.http_client.config.hostname = "http-host"
    host = database._get_databricks_host(connector, {})
    assert host == "http-host"


def test_get_databricks_host_from_http_client_offline_mode():
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    connector.connection.http_client.config.hostname = "http-host"
    host = database._get_databricks_host(
        db_connector=connector, db_connector_extra_args={}, offline_mode=True
    )
    assert host == "http-host"


def test_get_databricks_host_none():
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    host = database._get_databricks_host(connector, {})
    assert host is None


def test_get_databricks_host_accepts_offline_mode():
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    host = database._get_databricks_host(
        db_connector=connector, db_connector_extra_args={}, offline_mode=True
    )
    assert host is None


def test_get_databricks_token_from_extra_args():
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    token = database._get_databricks_token(connector, {"token": "12345"})
    assert token == "12345"


def test_get_databricks_token_from_bearer_header():
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    connector.connection.session.auth_provider = MagicMock()
    setattr(
        connector.connection.session.auth_provider,
        "_AccessTokenAuthProvider__authorization_header_value",
        "Bearer abc.def ",
    )
    token = database._get_databricks_token(connector, {})
    assert token == "abc.def"


def test_get_databricks_token_from_bearer_header_offline_mode():
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    connector.connection.session.auth_provider = MagicMock()
    setattr(
        connector.connection.session.auth_provider,
        "_AccessTokenAuthProvider__authorization_header_value",
        "Bearer abc.def ",
    )
    token = database._get_databricks_token(
        db_connector=connector, db_connector_extra_args={}, offline_mode=True
    )
    assert token == "abc.def"


def test_get_databricks_token_from_bearer_header_token_federation():
    """Another case for token retrieval, in newer databricks clients."""
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    connector.connection.session.auth_provider = MagicMock(
        external_provider={"_AccessTokenAuthProvider__authorization_header_value": "Bearer abc.def "}
    )
    del connector.connection.session.auth_provider._AccessTokenAuthProvider__authorization_header_value
    token = database._get_databricks_token(connector, {})
    assert token == "abc.def"


def test_get_databricks_token_from_bearer_header_token_federation_offline_mode():
    """Another case for token retrieval, in newer databricks clients."""
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    connector.connection.session.auth_provider = MagicMock(
        external_provider={"_AccessTokenAuthProvider__authorization_header_value": "Bearer abc.def "}
    )
    del connector.connection.session.auth_provider._AccessTokenAuthProvider__authorization_header_value
    token = database._get_databricks_token(
        db_connector=connector, db_connector_extra_args={}, offline_mode=True
    )
    assert token == "abc.def"


def test_get_databricks_token_none():
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    connector.connection.session.auth_provider = MagicMock()
    token = database._get_databricks_token(connector, {})
    assert token is None


def test_get_databricks_token_none_offline_mode():
    connector = MagicMock()
    connector.connection = _empty_databricks_connection()
    connector.connection.session.auth_provider = MagicMock()
    token = database._get_databricks_token(
        db_connector=connector, db_connector_extra_args={}, offline_mode=True
    )
    assert token is None


@pytest.mark.parametrize("qid", [None, ""])
def test_get_query_execution_metadata_returns_default_when_no_query_id(qid):
    connector = MagicMock()
    result = database.get_query_execution_metadata(connector, query_id=qid, db_connector_extra_args=None)
    assert isinstance(result, database.QueryExecutionMetadata)
    assert result == database.QueryExecutionMetadata()


@patch.object(database, "_get_query_metadata_snowflake", create=True)
@patch.object(database, "db_type_from_connector", return_value=database.SNOWFLAKE_DB_TYPE)
def test_get_query_execution_metadata_returns_default_when_offline_mode_snowflake(
    mock_from_conn, mock_snowflake
):
    connector = MagicMock()
    mock_snowflake.return_value = database.QueryExecutionMetadata(query_id="Q123", query_text="SELECT 1")

    got = database.get_query_execution_metadata(
        db_connector=connector, query_id="Q123", db_connector_extra_args={}, offline_mode=True
    )

    mock_from_conn.assert_not_called()
    mock_snowflake.assert_not_called()
    connector.execute.assert_not_called()
    assert got == database.QueryExecutionMetadata()


@pytest.mark.parametrize("lookback_minutes", (77, -77, 0))
@patch.object(database, "_get_query_metadata_snowflake", create=True)
@patch.object(database, "db_type_from_connector", return_value=database.SNOWFLAKE_DB_TYPE)
def test_get_query_execution_metadata_snowflake_delegates_to_helper(
    mock_from_conn, mock_snowflake, lookback_minutes
):
    connector = MagicMock()
    expected = database.QueryExecutionMetadata(query_id="Q123", query_text="SELECT 1")
    mock_snowflake.return_value = expected

    got = database.get_query_execution_metadata(
        connector,
        query_id="Q123",
        db_connector_extra_args={"query_history_lookback_minutes": lookback_minutes},
    )

    mock_snowflake.assert_called_once_with(
        db_connector=connector, query_id="Q123", lookback_minutes=lookback_minutes
    )
    assert got == expected


@patch.object(database, "_get_query_metadata_snowflake", create=True)
@patch.object(database, "db_type_from_connector", return_value=database.SNOWFLAKE_DB_TYPE)
def test_get_query_execution_metadata_snowflake_exception_returns_default(mock_from_conn, mock_snowflake):
    connector = MagicMock()
    mock_snowflake.side_effect = RuntimeError("boom")

    got = database.get_query_execution_metadata(connector, query_id="Q123", db_connector_extra_args={})

    assert isinstance(got, database.QueryExecutionMetadata)
    assert got == database.QueryExecutionMetadata()


@patch.object(database, "_get_query_metadata_databricks", create=True)
@patch.object(database, "_get_databricks_host", create=True)
@patch.object(database, "_get_databricks_token", create=True)
@patch.object(database, "db_type_from_connector", return_value=database.DATABRICKS_DB_TYPE)
def test_get_query_execution_metadata_databricks_delegates_correctly(
    mock_from_conn, mock_token, mock_host, mock_dbx
):
    connector = MagicMock()
    mock_host.return_value = "the-host"
    mock_token.return_value = "the-token"
    expected = database.QueryExecutionMetadata(query_id="Q999", query_text="SELECT * FROM t")
    mock_dbx.return_value = expected

    got = database.get_query_execution_metadata(
        connector, query_id="Q999", db_connector_extra_args={"token": "t"}
    )

    mock_host.assert_called_once_with(
        db_connector=connector, db_connector_extra_args={"token": "t"}, offline_mode=False
    )
    mock_token.assert_called_once_with(
        db_connector=connector, db_connector_extra_args={"token": "t"}, offline_mode=False
    )
    mock_dbx.assert_called_once_with(query_id="Q999", host="the-host", token="the-token")
    assert got == expected


@patch.object(database, "_get_query_metadata_databricks", create=True)
@patch.object(database, "_get_databricks_host", create=True)
@patch.object(database, "_get_databricks_token", create=True)
@patch.object(database, "db_type_from_connector", return_value=database.DATABRICKS_DB_TYPE)
def test_get_query_execution_metadata_returns_default_when_offline_mode_databricks(
    mock_from_conn, mock_token, mock_host, mock_dbx
):
    connector = MagicMock()
    mock_host.return_value = "the-host"
    mock_token.return_value = "the-token"
    mock_dbx.return_value = database.QueryExecutionMetadata(query_id="Q999", query_text="SELECT * FROM t")

    got = database.get_query_execution_metadata(
        db_connector=connector, query_id="Q999", db_connector_extra_args={"token": "t"}, offline_mode=True
    )

    mock_from_conn.assert_not_called()
    mock_host.assert_not_called()
    mock_token.assert_not_called()
    mock_dbx.assert_not_called()
    connector.execute.assert_not_called()

    assert got == database.QueryExecutionMetadata()


@patch.object(database, "_get_query_metadata_databricks", create=True)
@patch.object(database, "_get_databricks_host", create=True)
@patch.object(database, "_get_databricks_token", create=True)
@patch.object(database, "db_type_from_connector", return_value=database.DATABRICKS_DB_TYPE)
def test_get_query_execution_metadata_databricks_exception_returns_default(
    mock_from_conn, mock_token, mock_host, mock_dbx
):
    connector = MagicMock()
    mock_host.return_value = "the-host"
    mock_token.return_value = "the-token"
    mock_dbx.side_effect = ValueError("kaboom")

    got = database.get_query_execution_metadata(
        connector, query_id="Q9", db_connector_extra_args={"token": "t"}
    )

    mock_host.assert_called_once_with(
        db_connector=connector, db_connector_extra_args={"token": "t"}, offline_mode=False
    )
    mock_token.assert_called_once_with(
        db_connector=connector, db_connector_extra_args={"token": "t"}, offline_mode=False
    )
    mock_dbx.assert_called_once_with(query_id="Q9", host="the-host", token="the-token")
    assert isinstance(got, database.QueryExecutionMetadata)
    assert got == database.QueryExecutionMetadata()


@patch.object(database, "db_type_from_connector", return_value="other")
def test_get_query_execution_metadata_unknown_connector_returns_default(mock_from_conn):
    connector = MagicMock()
    got = database.get_query_execution_metadata(connector, query_id="QA", db_connector_extra_args={})
    assert isinstance(got, database.QueryExecutionMetadata)
    assert got == database.QueryExecutionMetadata()


def test_get_query_metadata_snowflake_returns_default_when_no_row():
    connector = MagicMock()
    connector.execute.return_value = None
    connector.fetchone.return_value = None

    result = database._get_query_metadata_snowflake(connector, query_id="Q123")

    connector.execute.assert_called_once()
    assert isinstance(result, database.QueryExecutionMetadata)
    assert result == database.QueryExecutionMetadata()


def test_get_query_metadata_snowflake_successful_query():
    now = datetime.datetime(2025, 1, 1)
    connector = MagicMock()
    connector.fetchone.return_value = (
        "Q123",  # query_id
        "SELECT 1",  # query_text
        "SUCCESS",  # execution_status
        now,  # start_time
        now,  # end_time
        None,  # error_code
        None,  # error_message
    )

    result = database._get_query_metadata_snowflake(connector, query_id="Q123")

    connector.execute.assert_called_once()
    assert result.query_id == "Q123"
    assert result.query_text == "SELECT 1"
    assert result.is_successful is True
    assert result.start_time == now
    assert result.end_time == now
    assert result.error is None


def test_get_query_metadata_snowflake_failed_query():
    now = datetime.datetime(2025, 1, 1)
    connector = MagicMock()
    connector.fetchone.return_value = (
        "Q456",
        "SELECT * FROM t",
        "FAILED_WITH_ERROR",
        now,
        now,
        "123",
        "Division by zero",
    )

    result = database._get_query_metadata_snowflake(connector, query_id="Q456")

    assert result.query_id == "Q456"
    assert result.query_text == "SELECT * FROM t"
    assert result.is_successful is False
    assert result.error == "123: Division by zero"


def test_get_query_metadata_snowflake_executes_expected_query_exactly():
    connector = MagicMock()
    connector.fetchone.return_value = None
    query_id = "123"

    database._get_query_metadata_snowflake(connector, query_id=query_id)

    executed_query = connector.execute.call_args[0][0]
    expected_query = (
        "SELECT "
        "QUERY_ID, QUERY_TEXT, EXECUTION_STATUS, START_TIME, END_TIME, ERROR_CODE, ERROR_MESSAGE "
        "FROM "
        "table(snowflake.information_schema.query_history()) "
        "WHERE "
        "QUERY_ID = '123' "
        ";"
    )
    assert executed_query == expected_query


def test_get_query_metadata_snowflake_executes_expected_query_exactly_with_lookback():
    connector = MagicMock()
    connector.fetchone.return_value = None
    query_id = "123"

    database._get_query_metadata_snowflake(connector, query_id=query_id, lookback_minutes=5)

    executed_query = connector.execute.call_args[0][0]
    expected_query = (
        "SELECT "
        "QUERY_ID, QUERY_TEXT, EXECUTION_STATUS, START_TIME, END_TIME, ERROR_CODE, ERROR_MESSAGE "
        "FROM "
        "table(snowflake.information_schema.query_history("
        "DATEADD('minute', -5, CURRENT_TIMESTAMP()), "
        "CURRENT_TIMESTAMP(), "
        "10000"
        ")) "
        "WHERE "
        "QUERY_ID = '123' "
        ";"
    )
    assert executed_query == expected_query


def test_get_query_metadata_snowflake_raises_for_status_propagates():
    connector = MagicMock()
    connector.fetchone.side_effect = RuntimeError("bad http")

    with pytest.raises(RuntimeError, match="bad http"):
        database._get_query_metadata_snowflake(connector, query_id="123")


@patch("astro_observe_sdk.utils.database.requests.get")
def test_get_query_metadata_databricks_builds_correct_request(mock_get):
    query_id = "Q123"
    host = "my-dbx-host"
    token = "tok123"
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"res": []}
    mock_get.return_value = mock_response

    database._get_query_metadata_databricks(query_id=query_id, host=host, token=token)

    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert kwargs["url"] == f"https://{host}/api/2.0/sql/history/queries"
    assert kwargs["headers"] == {"Authorization": f"Bearer {token}"}
    assert kwargs["params"] == [("filter_by.statement_ids", query_id)]


@patch("astro_observe_sdk.utils.database.requests.get")
def test_get_query_metadata_databricks_returns_default_if_empty_response(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"res": []}
    mock_get.return_value = mock_response

    result = database._get_query_metadata_databricks("Q1", "h", "t")

    assert isinstance(result, database.QueryExecutionMetadata)
    assert result == database.QueryExecutionMetadata()


@patch("astro_observe_sdk.utils.database.requests.get")
def test_get_query_metadata_databricks_without_timestamps(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "res": [
            {
                "query_id": "Q4",
                "query_text": "SELECT no_time",
                "status": "FINISHED",
                # no timestamps provided
            }
        ]
    }
    mock_get.return_value = mock_response

    result = database._get_query_metadata_databricks("Q4", "h", "t")

    assert result.query_id == "Q4"
    assert result.query_text == "SELECT no_time"
    assert result.is_successful is True
    assert result.start_time is None
    assert result.end_time is None
    assert result.error is None


@patch("astro_observe_sdk.utils.database.requests.get")
def test_get_query_metadata_databricks_success_with_timestamps(mock_get):
    start_ms = 1_600_000_000_000
    end_ms = 1_600_000_100_000
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "res": [
            {
                "query_id": "Q2",
                "query_text": "SELECT 1",
                "status": "FINISHED",
                "query_start_time_ms": start_ms,
                "query_end_time_ms": end_ms,
            }
        ]
    }
    mock_get.return_value = mock_response

    result = database._get_query_metadata_databricks("Q2", "h", "t")

    assert result.query_id == "Q2"
    assert result.query_text == "SELECT 1"
    assert result.is_successful is True
    assert result.start_time == datetime.datetime.fromtimestamp(start_ms / 1000, tz=datetime.timezone.utc)
    assert result.end_time == datetime.datetime.fromtimestamp(end_ms / 1000, tz=datetime.timezone.utc)
    assert result.error is None


@patch("astro_observe_sdk.utils.database.requests.get")
def test_get_query_metadata_databricks_failure_status(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "res": [
            {
                "query_id": "Q3",
                "query_text": "SELECT bad",
                "status": "FAILED",
                "error_message": "syntax error",
            }
        ]
    }
    mock_get.return_value = mock_response

    result = database._get_query_metadata_databricks("Q3", "h", "t")

    assert result.query_id == "Q3"
    assert result.query_text == "SELECT bad"
    assert result.is_successful is False
    assert result.error == "syntax error"


@patch("astro_observe_sdk.utils.database.requests.get")
def test_get_query_metadata_databricks_missing_query_id_falls_back(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"res": [{"query_text": "SELECT fallback"}]}
    mock_get.return_value = mock_response

    result = database._get_query_metadata_databricks("QX", "h", "t")

    assert result.query_id == "QX"
    assert result.query_text == "SELECT fallback"


@patch("astro_observe_sdk.utils.database.requests.get")
def test_get_query_metadata_databricks_raises_for_status_propagates(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = RuntimeError("bad http")
    mock_get.return_value = mock_response

    with pytest.raises(RuntimeError, match="bad http"):
        database._get_query_metadata_databricks("QZ", "h", "t")
