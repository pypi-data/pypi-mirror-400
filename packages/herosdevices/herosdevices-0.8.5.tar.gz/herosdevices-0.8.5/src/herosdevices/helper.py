"""Helper functions for writing hardware drivers."""

import hashlib
import importlib
import json
import logging
import re
import textwrap
from collections.abc import Callable, Iterable
from functools import wraps
from typing import Any

##############################################################
# extend logging mechanism
SPAM = 5
setattr(logging, "SPAM", 5)  # noqa: B010 #TODO: Why is this line necessary at all?
logging.addLevelName(levelName="SPAM", level=5)


class Logger(logging.Logger):
    """Extend logger to include a spam level for debugging device communication."""

    def setLevel(self, level: str | int, globally: bool = False) -> None:  # noqa: N802 D102
        if isinstance(level, str):
            level = level.upper()
        try:
            level = int(level)
        except ValueError:
            pass
        logging.Logger.setLevel(self, level)
        if globally:
            for logger in logging.root.manager.loggerDict.values():
                if not hasattr(logger, "setLevel"):
                    continue
                logger.setLevel(level)

    def spam(self, msg: str, *args, **kwargs) -> None:
        """Log a message with severity SPAM, even lower than DEBUG."""
        self.log(SPAM, msg, *args, **kwargs)


logging.setLoggerClass(Logger)
format_str = "%(asctime)-15s %(name)s: %(message)s"
logging.basicConfig(format=format_str)

log = logging.getLogger("herosdevices")


SI_PREFIX_EXP = {
    "Y": 24,
    "Z": 21,
    "E": 18,
    "P": 15,
    "T": 12,
    "G": 9,
    "M": 6,
    "k": 3,
    "h": 2,
    "base": 0,
    "d": -1,
    "c": -2,
    "m": -3,
    "u": -6,
    "n": -9,
    "p": -12,
    "f": -15,
    "a": -18,
    "z": -21,
    "y": -24,
}


def limits(lower: float, upper: float) -> Callable[[float], str | bool]:
    """Create a function which checks if a value is within the specified range.

    Args:
        lower: The lower bound of the valid range.
        upper: The upper bound of the valid range.

    Returns:
        A function that takes a value and returns True if within the range, or a message
        indicating it's out of range.
    """

    def check(val: float) -> str | bool:
        if val < lower or val > upper:
            return f"Value {val} is out of range [{lower}, {upper}]"
        return True

    return check


def limits_int(lower: int, upper: int) -> Callable[[int], str | bool]:
    """Create a function to check if a value is within a specified range and is an integer.

    Args:
        lower: The lower bound of the valid range.
        upper: The upper bound of the valid range.

    Returns:
        A function that takes a value and returns True if within the range and is an integer,
        or a message indicating why it's invalid.
    """

    def check(val: int) -> str | bool:
        if val < lower or val > upper:
            return f"Value {val} is out of range [{lower}, {upper}]"
        if val % 1 != 0:
            return f"Value {val} is not an integer"
        return True

    return check


def explicit(values: list[Any]) -> Callable[[Any], str | bool]:
    """Create a function to check if a value is in a list of allowed values.

    Args:
        values: A list of allowed values.

    Returns:
        A function that takes a value and returns True if within the list, or a message
        indicating it's not in the list.
    """

    def check(val: Any) -> bool | str:
        if val not in values:
            return f"Value {val} is not in list of allowed values {values}"
        return True

    return check


def extract_regex(pattern: str) -> Callable[[str], str]:
    """Create a function to extract a value from a string via regex pattern matching.

    Args:
        regex: regex pattern string.

    Returns:
        A function that takes a string and returns the first match group.
    """

    def match_str(input_string: str) -> str:
        match = re.search(pattern, input_string)

        if match:
            return match.group()
        return ""

    return match_str


def transform_unit(in_unit: str, out_unit: str) -> Callable[[float, bool], float]:
    """Create a function to transform a value from one unit to another using SI prefixes.

    Args:
        in_unit: The input unit (e.g., 'k' for kilo, 'm' for milli). Use 'base' for no prefix.
        out_unit: The output unit (e.g., 'k' for kilo, 'm' for milli). Use 'base' for no prefix.

    Returns:
        A function that transforms a given value from the input unit to the output unit,
        optionally allowing reverse transformation (second argument True).
    """
    if in_unit == "base":
        in_exp = 0
    else:
        in_exp = SI_PREFIX_EXP[in_unit[0]]
    if out_unit == "base":
        out_exp = 0
    else:
        out_exp = SI_PREFIX_EXP[out_unit[0]]
    multiplier = 10 ** (in_exp - out_exp)

    def transform(val: float, reverse: bool = False) -> float:
        if reverse:
            return val / multiplier
        return val * multiplier

    return transform


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """Recursively merge two dicts of dicts."""
    new_dict = dict1.copy()
    for k, v in dict2.items():
        if k in dict1 and isinstance(dict1[k], dict) and isinstance(v, dict):
            new_dict[k] = merge_dicts(new_dict[k], v)
        else:
            new_dict[k] = v
    return new_dict


def get_or_create_dynamic_subclass(base_cls: Any, *args: Any, **kwargs: Any) -> type:
    """Return a cached dynamic subclass of ``base_cls`` based on the input arguments.

    This helper generates a subclass of ``base_cls`` whose identity is determined by ``*args`` and ``**kwargs``.
    The argument signature is serialized into a hash, which is then used as both a cache key and the dynamic subclass
    name. If the subclass for a given argument combination already exists, it is returned from cache.

    The generated subclass replaces ``__new__`` with a dummy implementation to prevent recursive invocation of
    ``base_cls.__new__``.

    Args:
        base_cls: The base class to derive from. Must be passed positionally.
        *args: Positional values that should influence subclass identity.
        **kwargs: Keyword values that should influence subclass identity.

    Returns:
        A dynamically generated subclass of ``base_cls``.

    Raises:
        TypeError: If arguments cannot be serialized for hashing.
    """
    # normalize args+kwargs
    signature = json.dumps(
        {"args": args, "kwargs": kwargs},
        sort_keys=True,
        default=str,
    )
    arg_hash = hashlib.blake2s(signature.encode()).hexdigest()
    new_cls_name = f"{base_cls.__name__}_{arg_hash}"
    # generate cache
    generated = getattr(base_cls, "_generated_classes", {})
    if new_cls_name in generated:
        return generated[new_cls_name]

    # dummy __new__ method for subclasses
    def _no_new(subcls: type, *_a, **_kw) -> Callable:
        return object.__new__(subcls)

    # generate new class
    new_cls = type(
        new_cls_name,
        (base_cls,),
        {"__new__": _no_new},
    )
    # cache it
    if not hasattr(base_cls, "_generated_classes"):
        base_cls._generated_classes = {}
    base_cls._generated_classes[new_cls_name] = new_cls
    return new_cls


def add_class_descriptor(cls: type, attr_name: str, descriptor) -> None:  # noqa: ANN001
    """
    Add a descriptor to a class.

    This is a simple helper function which uses `setattr` to add an attribute to the class and then also calls
    `__set_name__` on the attribute.

    Args:
        cls: Class to add the descriptor to
        attr_name: Name of the attribute the descriptor will be added to
        descriptor: The descriptor to be added
    """
    setattr(cls, attr_name, descriptor)
    getattr(cls, attr_name).__set_name__(cls, attr_name)


def mark_driver(
    name: str | None = None,
    info: str | None = None,
    state: str = "unknown",
    additional_docs: list | None = None,
    requires: dict | None = None,
    product_page: str | None = None,
) -> Callable:
    """Mark a class as a driver.

    This decorator can be used to mark a class as a driver and attach meta data to it, which is then accessed by the
    sphinx documentation. All drivers marked with this decorator will be listed on the "Hardware" page. Wraps the
    ``__init__`` function of the decorated class to check if all required packages are installed.

    Args:
        state: State of the driver, can be "alpha" for very untested code "beta" for tested but under active development
            or "stable" for well tested and stable drivers.
        name: Name of the represented hardware as it should appear in the doc.
        info: Small info line which is shown as a subtitle in the doc.
        additional_docs: List of additional ``.rst`` files that are added to the documentation. For example to document
            complicated vendor library installation procedures.
        requires: List of additional packages that are required to use the driver, given in the form of a dictionary
            with the package name used in an import statement as key and a PyPi package name or url to the package as
            value. The import name is used to check if the required package is available.
        product_page: URL to the vendor product page
    """
    if additional_docs is None:
        additional_docs = []
    if requires is None:
        requires = {}

    def decorator(cls: type) -> type:
        cls.__driver_data__ = {  # type: ignore
            "state": state,
            "name": name,
            "info": info,
            "additional_docs": additional_docs,
            "requires": requires,
            "product_page": product_page,
        }

        def decorate_init(func: Callable) -> Callable:
            """Decorate __init__ function of class to check if all required modules are available."""

            @wraps(func)
            def decorated(*args, **kwargs) -> None:
                for import_name, pkg_name in requires.items():
                    try:
                        importlib.import_module(import_name)
                    except ModuleNotFoundError as e:
                        msg = f"\nPackage {pkg_name} is required for {cls.__name__} but is not installed.\n"
                        if url := re.findall(r"(?<!git\+)https?://\S+|www\.\S+", pkg_name):
                            msg += f"Please go to {url[0]} for installation instructions.\n"
                        else:
                            msg += f"Please install it with `uv pip install {pkg_name}`\n"
                        driver_page_url = (
                            f"https://herosdevices-dc5ccd.gitlab.io/hardware/generated/windfreak/{cls.__name__}.html"
                        )
                        msg += f"Also check the driver page {driver_page_url} if further steps are required."
                        # TODO: add a help string for docker container
                        raise ModuleNotFoundError(textwrap.indent(msg, "\t")) from e
                func(*args, **kwargs)

            return decorated

        cls.__init__ = decorate_init(cls.__init__)
        return cls

    return decorator


def cast_iterable(it: Iterable, target_type: Any) -> list:
    """Convert an iterable to a list of specified target type.

    Args:
        it: An iterable object containing elements to be converted.
        target_type: The type to which each element in the iterable should be converted.

    Returns:
        A list containing elements from the input iterable converted to the target type.

    Example:
        >>> cast_iterable([1, 2, 3], str)
        ['1', '2', '3']
        >>> cast_iterable(['1', '2', '3'], int)
        [1, 2, 3]
    """
    return [target_type(_) for _ in it]
