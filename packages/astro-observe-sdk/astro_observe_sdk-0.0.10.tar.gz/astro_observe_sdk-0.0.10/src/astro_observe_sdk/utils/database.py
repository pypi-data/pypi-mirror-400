"""Databases related utilities for the astro_observe_sdk package."""
from __future__ import annotations

import datetime
import logging
from typing import Any

import requests
from attr import define

from astro_observe_sdk.constants import DEFAULT_SNOWFLAKE_QUERY_HISTORY_LOOKBACK_MINUTES

log = logging.getLogger(__name__)

SNOWFLAKE_DB_TYPE = "snowflake"
DATABRICKS_DB_TYPE = "databricks"
SUPPORTED_DB_TYPES = (SNOWFLAKE_DB_TYPE, DATABRICKS_DB_TYPE)


@define
class QueryExecutionMetadata:
    """Metadata about a single query execution."""

    query_id: str | None = None
    query_text: str | None = None
    is_successful: bool = True
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
    error: str | None = None


@define
class QueryExecutionContext:
    """Context object containing all information needed to track a query execution."""

    query_id: str | None
    query_text: str | None
    query_job_namespace: str
    default_database: str | None
    default_schema: str | None
    query_execution_metadata: QueryExecutionMetadata
    db_type: str


def db_type_from_connector(db_connector: Any) -> str | None:
    """Return the database type inferred from a connector instance."""
    db_connector_name = type(db_connector).__name__
    if db_connector_name == "SnowflakeCursor":
        return SNOWFLAKE_DB_TYPE
    if db_connector_name in {"Cursor", "DatabricksCursor"}:
        return DATABRICKS_DB_TYPE
    return None


def db_type_from_query_job_namespace(query_job_namespace: str) -> str:
    """Return the database type inferred from a query job namespace."""
    db_type = query_job_namespace.split("://")[0]
    for supported_db_type in SUPPORTED_DB_TYPES:
        if db_type.lower() == supported_db_type:
            return supported_db_type
    return db_type.lower()


def resolve_query_execution_context(
    query_id: str | None,
    query_text: str | None,
    db_connector: Any,
    query_job_namespace: str | None,
    default_database: str | None,
    default_schema: str | None,
    db_connector_extra_args: dict[str, Any] | None,
) -> QueryExecutionContext:
    """Validate and resolve inputs into a unified QueryExecutionContext.

    This function normalizes the provided identifiers, metadata, and database
    connector information to build a complete QueryExecutionContext object.
    Missing values such as query ID, query text, or default database/schema are
    derived from the database connector where possible.

    Args:
        query_id: unique identifier for the query.
        query_text: SQL text of the query.
        db_connector: database connector object, used to extract metadata if not explicitly provided.
        query_job_namespace: namespace of the query job (e.g., "snowflake://org-acc").
        default_database: default database for query resolution.
        default_schema: default schema for query resolution.
        db_connector_extra_args: extra parameters used in metadata extraction with db_connector.

    Returns:
        populated query execution context.

    Raises:
        ValueError: If neither query ID nor query text is available, or if the
         query job namespace cannot be determined.
    """

    query_execution_metadata: QueryExecutionMetadata = QueryExecutionMetadata()
    db_connector_extra_args = db_connector_extra_args or {}

    # offline_mode allows passing a db_connector only for attribute extraction, without making
    # any calls through it (e.g., cursor.execute or API calls). This effectively treats the
    # connector as read-only and prevents issues like infinite recursion when users override
    # execute() to invoke the SDK in an automated way (e.g. within sitecustomize.py).
    offline_mode = bool(db_connector_extra_args.pop("offline_mode", False))

    if not query_id and db_connector:
        # This extraction must be first operation on db_connector, as later on we
        # might execute some queries and overwrite the last query_id in db_connector
        log.debug("query_id not provided, retrieving it from db_connector.")
        query_id = get_query_id(db_connector=db_connector, offline_mode=offline_mode)

    if not query_job_namespace and db_connector:
        log.debug("query_job_namespace not provided, retrieving it from db_connector.")
        query_job_namespace = get_query_job_namespace(
            db_connector=db_connector,
            db_connector_extra_args=db_connector_extra_args,
            offline_mode=offline_mode,
        )
    if not query_job_namespace:
        raise ValueError("`query_job_namespace` is required.")

    if not query_text and db_connector:
        log.debug("query_text not provided, retrieving it from db_connector.")
        query_execution_metadata = get_query_execution_metadata(
            db_connector=db_connector,
            query_id=query_id,
            db_connector_extra_args=db_connector_extra_args,
            offline_mode=offline_mode,
        )
        query_text = query_execution_metadata.query_text

    if not query_id and not query_text:
        raise ValueError("At least one of (`query_id`, `query_text`) must be present.")

    if db_connector and not all([default_database, default_schema]):
        log.debug("default database or schema not provided, retrieving it from db_connector.")
        database, schema = get_default_db_schema(db_connector=db_connector, offline_mode=offline_mode)
        default_database = default_database or database
        default_schema = default_schema or schema

    return QueryExecutionContext(
        query_id=query_id,
        query_text=query_text,
        query_job_namespace=query_job_namespace,
        default_database=default_database,
        default_schema=default_schema,
        query_execution_metadata=query_execution_metadata,
        db_type=db_type_from_query_job_namespace(query_job_namespace),
    )


def get_query_id(db_connector: Any, offline_mode: bool = False) -> str | None:
    """
    Retrieves the last query ID from the given database connector.

    Parameters:
        db_connector: database connector object that contain the last executed query ID.
        offline_mode: If `execute()` calls are allowed to be made with the `db_connector`.

    Returns:
        last query ID, if available; otherwise, None.
    """
    # offline_mode is not used now but may be relevant in the future
    return getattr(db_connector, "query_id", None) or getattr(db_connector, "sfqid", None)


def get_query_job_namespace(
    db_connector: Any,
    db_connector_extra_args: dict[str, Any],
    offline_mode: bool = False,
) -> str | None:
    """
    Retrieves query_job_namespace from the given database connector.

    Parameters:
        db_connector: database connector object
        db_connector_extra_args: extra parameters used in metadata extraction with db_connector.
        offline_mode: If `execute()` calls are allowed to be made with the `db_connector`.

    Returns:
        query_job_namespace if available; otherwise, None.
    """
    db_type = db_type_from_connector(db_connector)

    if db_type == SNOWFLAKE_DB_TYPE:
        if db_connector_extra_args.get("account_id"):
            account_id = db_connector_extra_args["account_id"]
        elif db_connector.connection.host:
            account_id = db_connector.connection.host.split(".snowflakecomputing.")[0]
        elif offline_mode:
            log.info(
                "Observe SDK's offline mode is enabled, Snowflake account_id "
                "could not be resolved without external calls."
            )
            return None
        else:  # will call .execute(), not allowed in offline mode
            account_id = db_connector.execute(
                "SELECT CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME();"
            ).fetchone()
            if not account_id:
                return None
            account_id = account_id[0]
        return f"snowflake://{account_id}"
    if db_type == DATABRICKS_DB_TYPE:
        host = _get_databricks_host(
            db_connector=db_connector,
            db_connector_extra_args=db_connector_extra_args,
            offline_mode=offline_mode,
        )
        if not host:
            return None
        return f"databricks://{host}"

    log.debug("query_job_namespace extraction for `db_type=%s` is not supported", db_type)
    return None


def get_default_db_schema(db_connector: Any, offline_mode: bool = False) -> tuple[str | None, str | None]:
    """
    Retrieves the default database and schema from the given db_connector.

    Parameters:
        db_connector: database connector object
        offline_mode: If `execute()` calls are allowed to be made with the `db_connector`.

    Returns:
        default db and schema if available; otherwise, tuple with two None values.
    """
    db_type = db_type_from_connector(db_connector)
    if db_type == SNOWFLAKE_DB_TYPE:
        db = db_connector.connection.database
        schema = db_connector.connection.schema

        if db and schema:
            return db, schema
        elif offline_mode:
            log.debug(
                "Offline mode is enabled, Snowflake default db or schema "
                "could not be resolved without external calls."
            )
            return db or None, schema or None
        else:  # will call .execute(), not allowed in offline mode
            res = db_connector.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA();").fetchone()
            if res:
                return db or res[0], schema or res[1]
            return db, schema

    if db_type == DATABRICKS_DB_TYPE:
        db = db_connector.connection.session.catalog
        schema = db_connector.connection.session.schema

        if db and schema:
            return db, schema
        elif offline_mode:
            log.debug(
                "Offline mode is enabled, Databricks default catalog or schema "
                "could not be resolved without external calls."
            )
            return db or None, schema or None
        else:  # will call .execute(), not allowed in offline mode
            res = db_connector.execute("SELECT current_catalog(), current_schema();").fetchone()
            if res:
                return db or res[0], schema or res[1]
            return db, schema

    log.debug("default db/schema extraction for `db_type=%s` is not supported", db_type)
    return None, None


def _get_databricks_host(
    db_connector: Any, db_connector_extra_args: dict[str, Any], offline_mode: bool = False
) -> str | None:
    """
    Retrieves the databricks host from the given db_connector.

    Parameters:
        db_connector: database connector object
        db_connector_extra_args: extra parameters used in metadata extraction with db_connector.
        offline_mode: If `execute()` calls are allowed to be made with the `db_connector`.

    Returns:
        databricks host if available; otherwise, tuple with two None values.
    """
    # offline_mode is not used now but may be relevant in the future
    host = (
        db_connector_extra_args.get("host")
        or db_connector.connection.session.host
        or db_connector.connection.http_client.config.hostname
    )
    if host:
        return str(host)
    return None


def _get_databricks_token(
    db_connector: Any, db_connector_extra_args: dict[str, Any], offline_mode: bool = False
) -> str | None:
    """
    Retrieves the databricks token from the given db_connector.

    Parameters:
        db_connector: database connector object
        db_connector_extra_args: extra parameters used in metadata extraction with db_connector.
        offline_mode: If `execute()` calls are allowed to be made with the `db_connector`.

    Returns:
        databricks token if available; otherwise, tuple with two None values.
    """
    # offline_mode is not used now but may be relevant in the future
    token = db_connector_extra_args.get("token")
    if not token:
        # Best effort guess on where the token is as we're digging into the private api that change
        token_key = "_AccessTokenAuthProvider__authorization_header_value"
        auth_provider = getattr(db_connector.connection.session, "auth_provider", None)
        raw_auth_header = getattr(auth_provider, token_key, None)
        if not raw_auth_header:
            auth_provider = getattr(auth_provider, "external_provider", {})
            if isinstance(auth_provider, dict):
                raw_auth_header = auth_provider.get(token_key, None)
            else:
                raw_auth_header = getattr(auth_provider, token_key, None)
        if isinstance(raw_auth_header, str) and raw_auth_header.startswith("Bearer "):
            token = str(raw_auth_header.removeprefix("Bearer ").strip()) or None
    if token:
        return str(token)
    return None


def get_query_execution_metadata(
    db_connector: Any,
    query_id: str | None,
    db_connector_extra_args: dict[str, Any],
    offline_mode: bool = False,
) -> QueryExecutionMetadata:
    """Retrieve query execution metadata from the database system.

    Uses the provided connector to fetch metadata about a query execution,
    including query text, timing, and error information. Supports Snowflake
    and Databricks; for unsupported systems, returns empty metadata.

    Args:
        db_connector: Database connector object.
        query_id: Unique identifier of the query.
        db_connector_extra_args: Optional extra parameters for the connector,
         used in Databricks host/token retrieval.
        offline_mode: If `execute()` calls are allowed to be made with the `db_connector`.

    Returns:
        Metadata about the query execution.
    """
    if not query_id:
        return QueryExecutionMetadata()
    if offline_mode:
        # Snowflake is always using execute() to get metadata and it's not allowed in offline_mode.
        # For databricks we do API call unrelated to db_connector, but for now let's keep offline mode consistent
        # - no external calls at all.
        log.info(
            "Observe SDK's offline mode is enabled, "
            "query execution metadata could not be resolved without external calls."
        )
        return QueryExecutionMetadata()
    db_type = db_type_from_connector(db_connector)
    try:
        if db_type == SNOWFLAKE_DB_TYPE:
            lookback_minutes = db_connector_extra_args.get(
                "query_history_lookback_minutes", DEFAULT_SNOWFLAKE_QUERY_HISTORY_LOOKBACK_MINUTES
            )
            return _get_query_metadata_snowflake(
                db_connector=db_connector, query_id=query_id, lookback_minutes=int(lookback_minutes)
            )
        if db_type == DATABRICKS_DB_TYPE:
            host = _get_databricks_host(
                db_connector=db_connector,
                db_connector_extra_args=db_connector_extra_args,
                offline_mode=offline_mode,
            )
            token = _get_databricks_token(
                db_connector=db_connector,
                db_connector_extra_args=db_connector_extra_args,
                offline_mode=offline_mode,
            )
            if host and token:
                return _get_query_metadata_databricks(query_id=query_id, host=host, token=token)
            if not host:
                log.warning(
                    "Databricks host could not be retrieved by Observe SDK. "
                    "Empty query metadata will be used."
                )
            if not token:
                log.warning(
                    "Databricks token could not be retrieved by Observe SDK. "
                    "Empty query metadata will be used."
                )
            return QueryExecutionMetadata()
        log.info("Observe SDK does not support querying extra metadata for `db_type=%s`", db_type)
    except Exception as e:
        log.warning(
            "Observe SDK encountered an error while retrieving additional metadata about SQL query. "
            "The process will continue with default empty values. Error details: %s",
            e,
        )
        log.debug("Error stacktrace:", exc_info=True)
    return QueryExecutionMetadata()


def _get_query_metadata_snowflake(
    db_connector: Any, query_id: str, lookback_minutes: int = 0
) -> QueryExecutionMetadata:
    """Retrieve query execution metadata from Snowflake.

    Executes a query against Snowflake's SNOWFLAKE.INFORMATION_SCHEMA.QUERY_HISTORY to
    gather metadata such as query text, status, execution times, and errors.

    Important:
        To limit overhead when querying the large QUERY_HISTORY table, this function only searches
        for queries that completed within the last N minutes (`lookback_minutes` arg). If the query has not
        finished within that time window or is still running, no metadata will be returned.

    https://docs.snowflake.com/en/sql-reference/account-usage#differences-between-account-usage-and-information-schema
    INFORMATION_SCHEMA.QUERY_HISTORY has no latency, so it's better than ACCOUNT_USAGE.QUERY_HISTORY
    https://docs.snowflake.com/en/sql-reference/functions/query_history
    SNOWFLAKE.INFORMATION_SCHEMA.QUERY_HISTORY() function seems the most suitable function for the job,
    we get history of queries executed by the user, and we're using the same credentials.

    Args:
        db_connector: Active Snowflake cursor object.
        query_id: Unique identifier of the query.
        lookback_minutes: Limit query metadata lookup to queries that finished in the last N minutes.
         Use `0` for no limit. Absolute value is used for negative integers.

    Returns:
        Metadata about the query execution.
    """
    date_filter = ""
    if lookback_minutes:
        date_filter = (
            f"DATEADD('minute', -{abs(lookback_minutes)}, CURRENT_TIMESTAMP()), "  # END_TIME_RANGE_START = N minutes ago
            "CURRENT_TIMESTAMP(), "  # END_TIME_RANGE_END = now, only completed queries are returned
            "10000"  # RESULT_LIMIT = 10000 , max allowed - query_id filter is applied after this is returned
        )
    query = (
        "SELECT "
        "QUERY_ID, QUERY_TEXT, EXECUTION_STATUS, START_TIME, END_TIME, ERROR_CODE, ERROR_MESSAGE "
        "FROM "
        f"table(snowflake.information_schema.query_history({date_filter})) "
        f"WHERE "
        f"QUERY_ID = '{query_id}' "
        f";"
    )
    db_connector.execute(query)
    row = db_connector.fetchone()
    if not row:
        log.info(
            "Observe SDK did not find query metadata in Snowflake for query_id=%s. "
            "The query may still be running or may have completed more than 5 minutes ago. "
            "Empty query metadata will be used.",
            query_id,
        )
        return QueryExecutionMetadata()
    log.debug("Retrieved query execution metadata: %s", str(row))
    return QueryExecutionMetadata(
        query_id=row[0],
        query_text=row[1],
        is_successful="failed" not in str(row[2]).lower(),
        start_time=row[3],
        end_time=row[4],
        error=f"{row[5]}: {row[6]}" if row[6] else None,
    )


def _get_query_metadata_databricks(query_id: str, host: str, token: str) -> QueryExecutionMetadata:
    """Retrieve query execution metadata from Databricks.

    Calls the Databricks SQL Query History API to fetch details about a query,
    including text, status, timing, and errors.

    Args:
        query_id: Unique identifier of the query.
        host: Databricks host URL.
        token: Databricks access token.

    Returns:
        Metadata about the query execution.
    """
    # https://docs.databricks.com/api/azure/workspace/queryhistory/list
    response = requests.get(
        url=f"https://{host}/api/2.0/sql/history/queries",
        headers={"Authorization": f"Bearer {token}"},
        params=[("filter_by.statement_ids", query_id)],
    )

    response.raise_for_status()

    data = response.json()
    if not data or not data.get("res"):
        log.info(
            "Observe SDK did not find query metadata in Databricks for query_id=%s. "
            "Empty query metadata will be used.",
            query_id,
        )
        return QueryExecutionMetadata()
    row = data["res"][0]
    log.debug("Retrieved query execution metadata: %s", str(row))
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
    if row.get("query_start_time_ms") and row.get("query_end_time_ms"):
        start_time = datetime.datetime.fromtimestamp(
            row["query_start_time_ms"] / 1000, tz=datetime.timezone.utc
        )
        end_time = datetime.datetime.fromtimestamp(row["query_end_time_ms"] / 1000, tz=datetime.timezone.utc)
    return QueryExecutionMetadata(
        query_id=row.get("query_id", query_id),
        query_text=row.get("query_text"),
        is_successful=row.get("status", "finished").lower() not in ("canceled", "failed"),
        start_time=start_time,
        end_time=end_time,
        error=row.get("error_message"),
    )
