"""User-facing methods to interact with the Metrics API"""

import logging
import os
from typing import Unpack

import pendulum

from astro_observe_sdk.clients.config import TypedCommonConfig
from astro_observe_sdk.clients.metrics import Metric, MetricCategory
from astro_observe_sdk.clients.metrics import log_metric as _log_metric
from astro_observe_sdk.constants import ASTRO_DEPLOYMENT_ID_ENV_VAR
from astro_observe_sdk.utils.airflow import get_task_instance_from_context
from astro_observe_sdk.utils.observe import generate_asset_id
from astro_observe_sdk.utils.openlineage import lineage_run_id

log = logging.getLogger(__name__)


def log_metric(
    name: str,
    value: float,
    asset_id: str | None = None,
    timestamp: pendulum.DateTime | None = None,
    **kwargs: Unpack[TypedCommonConfig],
) -> None:
    """
    Log a single metric to the Metrics API. Automatically pulls in task context.
    """
    log.debug("Observe SDK `log_metric` has been called.")

    deployment_id = os.getenv(ASTRO_DEPLOYMENT_ID_ENV_VAR)
    if not deployment_id:
        raise ValueError(
            "Deployment ID not found. This should be automatically set by Astro."
            f"Please set the {ASTRO_DEPLOYMENT_ID_ENV_VAR} environment variable."
        )

    ti = get_task_instance_from_context()
    asset_id = generate_asset_id(ti) if not asset_id else asset_id
    run_id = lineage_run_id(ti)

    log.debug("Logging metric `%s`=`%s` for asset `%s`", name, value, asset_id)
    metric = Metric(
        asset_id=asset_id,
        deployment_id=deployment_id,
        run_id=run_id,
        category=MetricCategory.CUSTOM,
        name=name,
        value=value,
        timestamp=timestamp,
    )

    _log_metric(metric, **kwargs)
    log.debug("Metric successfully sent to Observe API.")
