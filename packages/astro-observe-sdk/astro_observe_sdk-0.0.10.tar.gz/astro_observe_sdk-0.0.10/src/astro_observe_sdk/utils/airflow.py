"""Airflow related utilities for the astro_observe_sdk package."""
from typing import Any

from astro_observe_sdk.constants import AIRFLOW_V_3_0_PLUS

if AIRFLOW_V_3_0_PLUS:
    from airflow.sdk import get_current_context  # type: ignore
else:
    from airflow.operators.python import get_current_context  # type: ignore


def get_task_instance_from_context() -> Any:
    task_instance = get_current_context().get("task_instance")

    if not task_instance:
        raise ValueError(
            "Task instance not found in context. Please run this function within an Airflow task."
        )
    return task_instance
