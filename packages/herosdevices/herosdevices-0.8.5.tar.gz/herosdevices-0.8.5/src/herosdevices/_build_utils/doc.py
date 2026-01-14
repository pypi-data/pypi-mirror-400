import ast
import importlib
import inspect
import json
import re
import textwrap
from collections import OrderedDict
from enum import Enum
from pathlib import Path
from pkgutil import iter_modules
from typing import TYPE_CHECKING

from docstring_parser import parse

from herosdevices.helper import log

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator
    from types import ModuleType


def get_example_json_dict(examples_path: Path) -> dict[str, dict]:
    """Extract example json files from the examples directory and save them to a dict of lists.

    The examples are extracted by the ``classname`` key. Multiple examples for the same classname can exist.
    """
    json_dict: dict[str, dict] = {}
    for json_file in Path(examples_path).rglob("*.json"):
        with Path.open(json_file, "r") as f:
            content = json.load(f)
            if "classname" in content:
                if content["classname"] not in json_dict:
                    json_dict[content["classname"]] = {}
                json_dict[content["classname"]][json_file] = content
    return json_dict


def extract_arg_defs_from_call(source_code: str, func_name: str) -> tuple[set, set]:
    """Extract arguments that are passed to ``func_name`` and used in the source code by traversing the ast tree."""
    # Parse the source code into an AST
    tree = ast.parse(textwrap.dedent(source_code))

    # Traverse the AST to find Call nodes where the function is func_name
    passed_args = set()
    used_args = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check if the function being called is func_name
            if isinstance(node.func, ast.Attribute) and node.func.attr == func_name:
                # Extract the arguments as source code
                for keyword in node.keywords:
                    passed_args.add(keyword.arg)
                    if isinstance(keyword.value, ast.Name):
                        used_args.add(keyword.value.id)

    return passed_args, used_args


def iter_vendor_modules(paths: "list[Iterable[str]]") -> "Iterator[tuple]":
    for path in paths:
        for vendor_module_info in iter_modules(path):
            try:
                # This is a bit shitty to pick apart the chained modules but I couldn't care to make a new function...
                if "herosdevices/hardware" in vendor_module_info.module_finder.path:  # type: ignore
                    vendor_module = importlib.import_module(f"herosdevices.hardware.{vendor_module_info.name}")
                else:
                    vendor_module = importlib.import_module(f"herosdevices.core.{vendor_module_info.name}")
            except ModuleNotFoundError:
                log.exception("Could not load module %s due to missing imports", vendor_module_info.name)
                continue
            yield vendor_module, vendor_module_info


def extract_devices(module: "ModuleType") -> list[list]:
    """Find all devices in module that are decorated by :py:func:`herosdevices.helper.mark_driver`."""
    devices = []
    for member_name, member in inspect.getmembers(module):
        if inspect.isclass(member):
            if hasattr(member, "__driver_data__"):
                mand_args, opt_args = get_arguments(member)
                devices.append([member_name, member, mand_args, opt_args])
    return devices


def get_mandatory_args(obj: type, doc: dict, skip_bound_arg: bool = True) -> dict[str, dict]:
    """Get all mandatory args of a function.

    Uses individual ``Args:`` docstring to try to extract an example value for the arg.
    """
    args = OrderedDict(
        [
            (
                param.name,
                {
                    "type": param.annotation if param.annotation is not param.empty else "",
                    "desc": doc[param.name].split("Example:")[0] if param.name in doc else "",
                },
            )
            for param in inspect.signature(obj).parameters.values()
            if param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY) and param.default is param.empty
        ]
    )
    if skip_bound_arg and args:
        args.popitem(last=False)
    return args


def get_optional_args(obj: type, doc: dict) -> dict:
    """Get all optional args of a function.

    Uses individual ``Args:`` docstring to try to extract an example value for the arg.
    """
    return {
        param.name: {
            "type": param.annotation if param.annotation is not param.empty else "",
            "default": param.default,
            "desc": doc[param.name].split("Example:")[0] if param.name in doc else "",
        }
        for param in inspect.signature(obj).parameters.values()
        if param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY) and param.default is not param.empty
    }


def get_variadic_args(func: "Callable") -> list[str]:
    """Get all variadic args of a function."""
    return [
        param.name
        for param in inspect.signature(func).parameters.values()
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD) and not param.name.startswith("_")
    ]


def get_arguments(clss: type, source_meths: tuple = ("__call__", "__new__", "__init__")) -> tuple[dict, dict]:  # noqa: C901
    """Infer mandatory and optional arguments from the given ``source_meths``.

    This function tries to find also all required args or parent classes which need to be passed through variadic args.
    Therefore it scans the source code of the function for parent calls and uses that to infer which parent arguments
    are defined in the function and are not required by passing them as ``*args`` or ``**kwargs``.
    """
    mand_args: dict[str, dict] = {}
    opt_args: dict[str, dict] = {}
    doc = extract_args_from_docstring(clss)
    for meth_name in source_meths:
        try:
            meth = getattr(clss, meth_name)
        except AttributeError:
            continue

        mand_args |= get_mandatory_args(meth, doc)
        opt_args |= get_optional_args(meth, doc)
        if var_args := get_variadic_args(meth):
            # Only if variadic args are passed arguments can be sneaked by us
            # check if parameters get fixed in constructor
            try:
                source = inspect.getsource(meth)
                fixed_args, used_args = extract_arg_defs_from_call(source, meth_name)
                if not used_args.intersection(set(var_args)):
                    # check if the function even pases the var_args to the parent. If not, we don't have to look further
                    continue
                result = re.search(r"kwargs\[[\"'](.*)[\"']\]\s?=.*", source)
                fixed_args.update(result.groups() if result is not None else [])
            except TypeError:
                # can not get source code, maybe c function or wrapper, ignore we can not learn more here
                log.debug(
                    "Can't find source code for %s.%s, not looking for argument definitions here.",
                    clss.__name__,
                    meth_name,
                )
                fixed_args = set()

            for parent_clss in clss.__bases__:
                if parent_clss is not object:
                    super_mand_args, super_opt_args = get_arguments(parent_clss, (meth_name,))

                    # remove fixed parameters
                    for fixed_param in fixed_args:
                        for args in [super_mand_args, super_opt_args]:
                            if fixed_param in args:
                                del args[fixed_param]

                    mand_args.update(super_mand_args)
                    opt_args.update(super_opt_args)

    return mand_args, opt_args


def extract_args_from_docstring(obj: type) -> dict:
    """Extract ``Args:`` from docstring of a function or class."""

    def clean_desc(desc: str | None) -> str:
        if desc is None:
            return ""
        return desc.replace("\n", " ").strip()

    result: dict[str, str] = {}
    for obj_res in reversed(obj.mro()):
        if (doc_str := obj_res.__doc__) is not None:
            result |= {param.arg_name: clean_desc(param.description) for param in parse(doc_str).params}
        if hasattr(obj_res, "__init__"):
            if (doc_str := obj_res.__init__.__doc__) is not None:  # type: ignore[misc]
                result |= {param.arg_name: clean_desc(param.description) for param in parse(doc_str).params}
        if hasattr(obj_res, "__new__"):
            if (doc_str := obj_res.__new__.__doc__) is not None:
                result |= {param.arg_name: clean_desc(param.description) for param in parse(doc_str).params}

    return result


def get_example_arg_dict(device: type, mand_args: dict, opt_args: dict) -> dict:  # noqa: C901
    """Infer the example "arguments" dict used for building the json string from documentation and signatures."""
    doc = extract_args_from_docstring(device)
    arguments = {}
    for arg_name, arg_info in mand_args.items():
        try:
            arg_doc = doc[arg_name].split("Example:")[1].strip().replace("true", "True").replace("false", "False")
            arguments[arg_name] = ast.literal_eval(arg_doc)
        except (KeyError, IndexError, SyntaxError, ValueError) as e:
            if isinstance(e, SyntaxError):
                msg = f'Could not infer example value of argument {arg_name} of device {device}. Strings wrapped in ""?'
                log.warning(msg)
            elif isinstance(e, ValueError):
                msg = f"Could not infer example value of argument {arg_name} of device {device}. Syntax error\
                        or non-literal detected"
                log.warning(msg)
            # not documented or does not have an example
            arguments[arg_name] = f"{arg_info['type']}"
    for arg_name, arg_info in opt_args.items():
        try:
            arg_doc = doc[arg_name].split("Example:")[1].strip().replace("true", "True").replace("false", "False")
            arguments[arg_name] = ast.literal_eval(arg_doc)
        except (KeyError, IndexError, SyntaxError, ValueError) as e:
            if isinstance(e, SyntaxError):
                msg = f'Could not infer example value of argument {arg_name} of device {device}. Strings wrapped in ""?'
                log.warning(msg)
            elif isinstance(e, ValueError):
                msg = (
                    f"Could not infer example value of argument {arg_name} of device {device}. Syntax error "
                    "or non-literal detected"
                )
                log.warning(msg)
            # not documented or does not have an example
            if type(arg_info["default"]) is bytes:
                arguments[arg_name] = arg_info["default"].decode()
            elif isinstance(arg_info["default"], Enum):
                arguments[arg_name] = arg_info["default"].value
            else:
                arguments[arg_name] = arg_info["default"]
    return arguments
