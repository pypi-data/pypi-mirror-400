import logging

from astro_observe_sdk.constants import __version__, AIRFLOW_LOGGING_LEVEL
from astro_observe_sdk.lineage import log_query, log_lineage
from astro_observe_sdk.metrics import log_metric

__all__ = ["__version__", "log_metric", "log_query", "log_lineage"]

logger = logging.getLogger("astro_observe_sdk")
logger.setLevel(AIRFLOW_LOGGING_LEVEL)
