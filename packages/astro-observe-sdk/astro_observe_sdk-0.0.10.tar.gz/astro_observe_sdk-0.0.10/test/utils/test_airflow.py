import pytest
from unittest.mock import patch, MagicMock

from astro_observe_sdk.utils.airflow import get_task_instance_from_context


def test_get_task_instance_from_context():
    fake_ti = MagicMock()
    with patch(
        "astro_observe_sdk.utils.airflow.get_current_context", return_value={"task_instance": fake_ti}
    ):
        assert get_task_instance_from_context() is fake_ti


def test_get_task_instance_from_context_raises():
    with patch("astro_observe_sdk.utils.airflow.get_current_context", return_value={}):
        with pytest.raises(ValueError, match="Task instance not found"):
            get_task_instance_from_context()
