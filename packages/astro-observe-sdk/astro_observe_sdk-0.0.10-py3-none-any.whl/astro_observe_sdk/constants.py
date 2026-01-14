"""Contains constants useful to the SDK."""

from airflow import __version__ as AIRFLOW_VERSION
from airflow.configuration import conf
from airflow.providers.openlineage import __version__ as OPENLINEAGE_PROVIDER_VERSION

__version__ = "0.0.10"

AIRFLOW_V_3_0_PLUS = AIRFLOW_VERSION >= "3.0.0"
AIRFLOW_LOGGING_LEVEL = conf.get("logging", "logging_level", fallback="INFO")

ASTRO_API_BASE_URL_ENV_VAR = "ASTRO_API_BASE_URL"
ASTRO_ORGANIZATION_ID_ENV_VAR = "ASTRO_ORGANIZATION_ID"
ASTRO_DEPLOYMENT_ID_ENV_VAR = "ASTRO_DEPLOYMENT_ID"
ASTRO_DEPLOYMENT_NAMESPACE_ENV_VAR = "ASTRO_DEPLOYMENT_NAMESPACE"
OBSERVE_API_TOKEN_ENV_VAR = "OBSERVE_API_TOKEN"

OPENLINEAGE_URL_ENV_VAR = "OPENLINEAGE_URL"
OPENLINEAGE_PRODUCER = f"https://github.com/astronomer/observe-sdk/tree/{__version__}"

DEFAULT_SNOWFLAKE_QUERY_HISTORY_LOOKBACK_MINUTES = 5

if AIRFLOW_V_3_0_PLUS and (OPENLINEAGE_PROVIDER_VERSION < "2.4.0"):
    raise RuntimeError("For Airflow 3, Observe SDK requires `apache-airflow-providers-openlineage>=2.4.0`")
