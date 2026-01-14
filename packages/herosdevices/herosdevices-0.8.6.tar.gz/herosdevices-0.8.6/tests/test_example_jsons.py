"""Tests for generated and provided example json BOSS files/strings."""

import importlib
import logging
from pathlib import Path

import pytest
from pyftdi.usbtools import UsbToolsError
from pyvisa.errors import VisaIOError

import src.herosdevices._build_utils.doc as doc_utils
from src.herosdevices import core, hardware

logger = logging.getLogger(__name__)

IGNORE_EXCEPTIONS = (PermissionError, ModuleNotFoundError, OSError, UsbToolsError, RuntimeError, VisaIOError)
FILTER_ERRORS = ("windows", "not reachable", "no backend")
BROKEN_DEVICES = ["ADS1256"]
TYPE_DEFAULT_MAPPING = {
    "<class 'dict'>": {"default": {}},
    "<class 'str'>": "",
    "<class 'list'>": [],
    "<class 'int'>": 0,
    "<class 'float'>": 0.0,
    "<class 'bool'>": False,
    "<class 'set'>": set(),
    "<class 'tuple'>": (),
}


@pytest.mark.filterwarnings("ignore: Exception ignored in")
def test_example_folder_jsons() -> None:
    """Test initialization of device drivers with the example jsons in the /example folder."""
    examples = doc_utils.get_example_json_dict(Path(__file__).resolve().parent / "../examples")
    for cls_path, cls_examples in examples.items():
        for example_file, example in cls_examples.items():
            assert "_id" in example
            assert "classname" in example
            module_name, _, cls_name = cls_path.rpartition(".")
            module = importlib.import_module(f"src.{module_name}")
            skip_device = False
            cls = getattr(module, cls_name)
            for value in example["arguments"].values():
                if isinstance(value, str):
                    if value.startswith(("herosdevices.", "$")):
                        # Can't test devices that rely on other devices
                        skip_device = True
                        break
            if not skip_device:
                try:
                    cls(**example["arguments"])
                except IGNORE_EXCEPTIONS:
                    # The init wants to connect to
                    logger.info("Skipping %s because it requires the physical device for init.", example_file)
                except TypeError as e:
                    msg = f"Error in {example_file} arguments: {e}"
                    raise TypeError(msg) from e


@pytest.mark.filterwarnings("ignore: Exception ignored in")
def test_generated_jsons() -> None:  # noqa: C901
    """Test initialization of device drivers with the example jsons in the /example folder."""
    for vendor_module, _ in doc_utils.iter_vendor_modules([hardware.__path__, core.__path__]):
        devices = doc_utils.extract_devices(vendor_module)
        for device_info in devices:
            skip_device = False
            cls = device_info[1]
            args, kwargs = doc_utils.get_arguments(cls)
            arguments = doc_utils.get_example_arg_dict(cls, args, kwargs)
            for key, value in arguments.items():
                if isinstance(value, str):
                    if value in TYPE_DEFAULT_MAPPING:
                        arguments[key] = TYPE_DEFAULT_MAPPING[value]
                    elif value.startswith(("herosdevices.", "$")):
                        # Can't test devices that rely on other devices
                        skip_device = True
                        break
            try:
                if cls.__name__ not in BROKEN_DEVICES and not skip_device:
                    cls(**arguments)
            except IGNORE_EXCEPTIONS:
                # The init wants to connect to the physical device, ignore.
                pass
            except Exception as e:
                if not any((filter_str in repr(e).lower()) for filter_str in FILTER_ERRORS):
                    raise
