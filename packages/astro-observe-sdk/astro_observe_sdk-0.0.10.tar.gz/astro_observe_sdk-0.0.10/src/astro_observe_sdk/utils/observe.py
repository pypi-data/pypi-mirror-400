"""Observe related utilities for the astro_observe_sdk package."""

import os
from typing import Any

from astro_observe_sdk.constants import ASTRO_DEPLOYMENT_NAMESPACE_ENV_VAR


def generate_asset_id(task_instance: Any) -> str:
    """
    Uses the current task context to generate an asset ID.
    """
    namespace = os.getenv(ASTRO_DEPLOYMENT_NAMESPACE_ENV_VAR)
    dag_id = task_instance.dag_id
    task_id = task_instance.task_id

    asset_id = f"{namespace}.{dag_id}.{task_id}"
    return asset_id
