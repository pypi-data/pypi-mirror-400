from unittest.mock import MagicMock

from astro_observe_sdk.utils.observe import generate_asset_id


def test_generate_asset_id(setup_env):
    task_instance = MagicMock(dag_id="example_dag", task_id="transform_task")
    assert generate_asset_id(task_instance) == "test-deployment-namespace.example_dag.transform_task"
