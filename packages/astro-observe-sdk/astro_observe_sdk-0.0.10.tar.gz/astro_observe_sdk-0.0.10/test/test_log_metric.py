from astro_observe_sdk.metrics import log_metric


def test_log_metric(mocker, setup_env):
    _log_metric_mock = mocker.patch("astro_observe_sdk.metrics._log_metric")
    _log_metric_mock.return_value = None
    _get_task_instance_from_context = mocker.patch("astro_observe_sdk.metrics.get_task_instance_from_context")
    _get_task_instance_from_context.return_value = None

    _generate_asset_id = mocker.patch("astro_observe_sdk.metrics.generate_asset_id")
    _generate_asset_id.return_value = "test_asset_id"
    _get_lineage_run_id = mocker.patch("astro_observe_sdk.metrics.lineage_run_id")
    _get_lineage_run_id.return_value = "test_run_id"

    log_metric("test_metric", 1.0)

    assert _log_metric_mock.call_count == 1
    assert _generate_asset_id.call_count == 1
    assert _get_lineage_run_id.call_count == 1
