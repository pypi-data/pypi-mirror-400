"""Test the DisplayDeviceTemplate."""

import pytest

from src.herosdevices.core.templates.display import DisplayDeviceTemplate

default_config = {
    "default": {
        "val": "test",
        "ch0": {
            "coupling": 0,
        },
    }
}

default_metadata = {"path": "test", "nested": {"val": 1}}


@pytest.fixture
def instance() -> DisplayDeviceTemplate:
    """
    Create a DisplayDeviceTemplate instance with default configuration.

    This fixture initializes a DisplayDeviceTemplate with predefined default
    configuration values and returns the instance for testing purposes.

    Returns:
        Initialized DisplayDeviceTemplate instance.
    """
    DisplayDeviceTemplate.default_config_dict = {"val": "false", "val2": "test"}
    return DisplayDeviceTemplate(config_dict=default_config)


def test_update_config(instance: DisplayDeviceTemplate) -> None:
    """
    Test updating configuration and resetting to default.

    Args:
        instance: The DisplayDeviceTemplate instance to test.
    """
    assert instance.get_configuration() == {"val2": "test"} | default_config["default"]

    new_conf = {"test": default_config["default"], "default": {"val": "test2"}}
    instance.update_configuration(new_conf)
    assert instance.get_configuration() == {"val2": "test"} | default_config["default"] | {"val": "test2"}
    instance.configure("test")
    assert instance.get_configuration() == {"val2": "test"} | default_config["default"]
