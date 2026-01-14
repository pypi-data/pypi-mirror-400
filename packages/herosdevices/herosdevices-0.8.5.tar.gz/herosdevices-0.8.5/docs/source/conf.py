"""Documentation configuration file for sphinx."""  # noqa:INP001

import datetime
import importlib
import importlib.metadata
import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import requests
import tomllib
from docstring_parser import parse
from sphinx.ext.napoleon.docstring import GoogleDocstring
from sphinx.util import logging

import herosdevices._build_utils.doc as doc_utils
from herosdevices import core, hardware

if TYPE_CHECKING:
    from types import ModuleType
    from typing import Any

    from sphinx.application import Sphinx

log = logging.getLogger(__name__)

# Add the project's src directory to sys.path
sys.path.insert(0, str(Path("../../src").resolve()))

# -- Project information -----------------------------------------------------
pyproject_path = Path(__file__).parents[2] / "pyproject.toml"

with pyproject_path.open("rb") as f:
    pyproject_data = tomllib.load(f)

project = pyproject_data["project"]["name"]


def get_version() -> str:
    """Get version from dynamic versioning."""
    try:
        result = subprocess.run(
            ["hatch", "version"],  # noqa: S607
            stdout=subprocess.PIPE,
            check=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        log.exception("Failed to get version from hatch: %s")
        return "unknown"


release = get_version()

version = release

# Extract author names
authors = [author["name"] for author in pyproject_data["project"]["authors"]]

# Build copyright
project = "Heros Devices"
year = datetime.datetime.now(tz=datetime.UTC).year
authors_str = ", ".join(authors)
copyright = f"{year}, {authors_str}"  # noqa: A001
author = authors_str

# -- General configuration ---------------------------------------------------

sys.path.append(str(Path("_ext").resolve()))
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.inheritance_diagram",
    "autoapi.extension",
    "sphinx.ext.napoleon",  # Support for Google and NumPy style docstrings
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.mathjax",  # Enable MathJax for LaTeX-style math
    "sphinx.ext.todo",  # Enable todo lists
    "sphinx_autodoc_typehints",  # Handle type hints in documentation
    "sphinx.ext.intersphinx",
    "sphinx_tabs.tabs",  # make tabbed doc menus
    "sphinx_copybutton",  # button to copy code blocks
    "collapse",
    "driverbox",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_static_path = ["../_static"]
# Furo theme options
html_theme_options = {
    "light_logo": "logo.svg",
    "dark_logo": "logo.svg",
    "sidebar_hide_name": False,
}
html_css_files = [
    "css/custom.css",
]

# Autodoc settings
autoclass_content = "both"
autodoc_default_options = {
    "members": None,
    "member-order": "bysource",
    "show-inheritance": None,
    "private-members": None,
    "inherited-members": None,
}

autodoc_mock_imports = ["serial", "ids_peak", "toptica", "picosdk", "dcamsdk4"]
# -- AutoAPI configuration ---------------------------------------------------
autoapi_options = ["members", "undoc-members", "show-inheritance", "inherited-members"]
autoapi_type = "python"
autoapi_dirs = ["../../src"]  # Path to your source code
autoapi_add_toctree_entry = True  # Avoid duplicate toctree entries
autoapi_keep_files = False  # Keep intermediate reStructuredText files

# todo conf
todo_include_todos = True

intersphinx_mapping = {
    "herostools": ("https://herostools-0faae3.gitlab.io/", None),
    "boss": ("https://boss-eb4966.gitlab.io/", None),
    "heros": ("https://heros-761c0f.gitlab.io/", None),
    "atomiq": ("https://atomiq-atomiq-project-515d34b8ff1a5c74fcf04862421f6d74a00d9de1b.gitlab.io/", None),
}

graphviz_output_format = "svg"
inheritance_graph_attrs = {"rankdir": "TB", "size": '""'}
inheritance_node_attrs = {
    "style": '"rounded,filled"',
    "penwidth": "2",
    "fillcolor": '"#5fabe827"',
    "color": '"#5fabe8"',
}
inheritance_edge_attrs = {"color": '"#5fabe8"', "penwidth": "2", "arrowsize": "1", "dir": '"back"'}

DEVICE_TOC = False  # Include a ToC of all devices on the Hardware page


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder extension to handle numpy int64 used in some type hints for sinara devices."""

    def default(self, o: "Any") -> "Any":  # noqa: D102
        if isinstance(o, np.int64):
            return int(o)
        return super().default(o)


def get_default_installed_pkgs() -> list[str]:
    """Get packages listed in pyproject.toml requirements (ignore "doc" and "dev" requirements)."""
    raw_pkgs = importlib.metadata.requires("herosdevices")
    pkgs = []
    for pkg in raw_pkgs:
        parts = pkg.split(";")
        if len(parts) > 1:
            if any(x in parts[1] for x in ["dev", "docs"]):
                continue
        pkgs.append(re.split(r"[><=]", parts[0])[0])
    return pkgs


def pad_rst_content(content: str | list, levels: int) -> str:
    """Add indentation to rst content."""
    if type(content) is str:
        content = content.split("\n")
    return "\n".join([f"{' ' * 3 * levels}{line}" for line in content]) + "\n"


def make_table(header: str, content: str, title: str, colsize: list | tuple) -> str:
    """Build a table in rst format."""
    out = f".. list-table:: {title}\n   :widths: {' '.join(colsize)}\n   :header-rows: 1\n\n"
    for row in [header, *content]:
        for i, data in enumerate(row):
            prefix = "   * - " if i == 0 else "     - "
            out += f"{prefix}{data}\n"
    return out


def build_jsons_from_examples(app: "Sphinx", class_paths: list[str]) -> str:
    """Build json examples rst content from dictionary of examples."""
    json_examples = doc_utils.get_example_json_dict(app.srcdir / "../../examples/")
    content = ""
    processed_files = []
    for class_path in class_paths:
        if class_path in json_examples:
            for path, example in json_examples[class_path].items():
                if path not in processed_files:
                    # If some of the class paths are the same, avoid duplicating the example
                    processed_files.append(path)
                    content += ".. code-block:: json\n\n"
                    json_str = json.dumps(example, indent=4, cls=NumpyEncoder).replace("Infinity", "1e999")
                    content += pad_rst_content(json_str, 1)
                    content += f"\n:sup:`from examples{str(path).split('examples')[-1]}` \n\n"
    return content


def build_json_repr(device: type, mand_args: dict, opt_args: dict) -> str:
    """Build an example json string for use with BOSS.

    The example arguments are inferred from the ``Args:`` documentation of the device, if an ``Example:`` is present for
    a given arg. If not, the default value (for keyword args) or a string of the type name (for positional args) is
    used.
    """
    arguments = doc_utils.get_example_arg_dict(device, mand_args, opt_args)
    # Build the JSON structure
    json_structure = {
        "_id": f"my_{device.__name__}",
        "classname": f"{device.__module__}.{device.__name__}",
        "arguments": arguments,
    }

    # Convert to JSON string
    json_str = json.dumps(json_structure, indent=4, cls=NumpyEncoder).replace("Infinity", "1e999")

    optional_lines = []
    mandatory_lines = []
    in_args = False
    for i, line in enumerate(json_str.split("\n")):
        if '"arguments":' in line:
            in_args = True
        elif in_args:
            for key in opt_args:
                if f'"{key}":' in line:
                    optional_lines.append(f"{i + 1}")
                    break
            for key in mand_args:
                if f'"{key}":' in line:
                    mandatory_lines.append(f"{i + 1}")
                    break

    lines = ".. code-block:: json\n\n"
    lines += pad_rst_content(json_str, 1)
    lines += "\n:sup:`generated from signature`"
    return lines


def build_device_link(device_name: str, device: type, device_html: str | Path) -> str:
    """Construct the rst content to generate a link box to a driver on the hardware page."""
    device_info = device.__driver_data__
    if device_info["name"]:
        device_name = device_info["name"]
    content = f".. driverbox:: {device_name}\n"
    if device_info["info"]:
        content += f"   :summary: {device_info['info']}\n"
    if device_info["state"] == "stable":
        content += "   :badge: good\n"
    elif device_info["state"] == "beta":
        content += "   :badge: warning\n"
    elif device_info["state"]:
        content += "   :badge: bad\n"
    content += f"   :badgetext: {device_info['state']}\n"
    content += f"   :ref: {device_html}\n\n"
    return content


def check_link_alive(url: str) -> int:
    """Check if the given URL returns a successful response status code."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0"}
        response = requests.head(url, timeout=2.0, headers=headers)
    except requests.RequestException:
        return 408
    return response.status_code


def build_device_page(  # noqa: C901
    app: "Sphinx",
    vendor_module: "ModuleType",
    vendor_name: str,
    device_name: str,
    device: type,
    mand_args: dict,
    opt_args: dict,
) -> str:
    """Build a collapsible doc tab based on driver information and the driver class itself."""
    device_info = device.__driver_data__
    if device_info["name"]:
        device_name = device_info["name"]
    full_class_path = f"{device.__module__}.{device.__name__}"
    vendor_class_path = f"{vendor_module.__name__}.{device.__name__}"

    content = f"{device_name}\n{''.join(['='] * len(device_name))}\n\n"

    device_quality = device_info["state"] if device_info["state"] else "alpha"
    if device_info["product_page"]:
        status = check_link_alive(device_info["product_page"])
        if status == 403:  # noqa: PLR2004
            log.warning(
                "Access to product page of %s %s (%s) denied, check manually if alive!",
                vendor_name,
                device_name,
                device_info["product_page"],
            )
        elif status < 200 or status >= 300:  # noqa: PLR2004
            log.error(
                "Link to product page of %s %s (%s) is dead!", vendor_name, device_name, device_info["product_page"]
            )
        content += pad_rst_content(f"**From:** `{vendor_name} <{device_info['product_page']}>`_\n", 0)
    else:
        content += pad_rst_content(f"**From:** {vendor_name}\n", 0)

    content += pad_rst_content(f"**Class:** :py:class:`{full_class_path}`\n\n", 0)
    content += pad_rst_content(f"**Driver Quality Index:** {device_quality}\n\n", 0)
    if device_info["requires"]:
        default_pkgs = get_default_installed_pkgs()
        required_pkgs = {k: v for k, v in device_info["requires"].items() if v not in default_pkgs}
        if required_pkgs:
            content += pad_rst_content(".. admonition:: Requires the following packages \n", 0)
            for key, desc in required_pkgs.items():
                if url_list := re.findall(r"https?://\S+|www\.\S+", desc):
                    content += pad_rst_content(f"`{key} <{url_list[0]}>`_,", 1)
                else:
                    url = f"https://pypi.org/project/{desc}"
                    content += pad_rst_content(f"`{desc} <{url}>`_,", 1)
            content = content.rstrip().rstrip(",")
            content += "\n\n"

    if device_info["additional_docs"]:
        for additional_doc in device_info["additional_docs"]:
            content += pad_rst_content(f".. include:: {additional_doc}", 0)
    if device.__doc__ is not None:
        if doc_str := parse(device.__doc__).description:
            parsed_docstring = GoogleDocstring(doc_str, app.config, app, "class").lines()
            content += pad_rst_content(parsed_docstring, 0)
            content += "\n"
    content += pad_rst_content(".. tabs:: \n\n", 0)
    content += pad_rst_content(".. tab:: Arguments\n\n", 1)
    content += pad_rst_content(
        f"Bold arguments are mandatory. For more information on the listed arguments refer to the class\
             documentation: :py:class:`{full_class_path}` If parameters appear in this\
             list but not in the class definition, please recursively check the linked base classes for the\
             definition of the parameter.\n\n",
        2,
    )
    content += (
        pad_rst_content(
            make_table(
                ["Argument", "Type", "Default Value", "Description"],
                [[f"**{key}**", f"**{val['type']}**", "", val["desc"]] for key, val in mand_args.items()]
                + [[key, str(val["type"]), str(val["default"]), val["desc"]] for key, val in opt_args.items()],
                "",
                ["50", "50", "50", "100"],
            ),
            2,
        )
        + "\n"
    )

    content += pad_rst_content(".. tab:: Example JSON for BOSS\n", 1)
    content += pad_rst_content(
        f"The following JSON strings can be used to start a HERO device representation of \
            :py:class:`{device.__name__} <{full_class_path}>` using \
            `BOSS <https://boss-eb4966.gitlab.io/>`_.\n",
        2,
    )
    content += pad_rst_content(build_jsons_from_examples(app, [full_class_path, vendor_class_path]), 2)
    content += pad_rst_content(build_json_repr(device, mand_args, opt_args), 2)
    content += pad_rst_content(".. tab:: Inheritance\n\n", 1)
    content += pad_rst_content(f".. inheritance-diagram:: {device.__module__}.{device.__name__}\n", 2)
    return content


def build_hardware_pages(app: "Sphinx") -> None:
    """Build the main hardware overview page with all device drivers."""
    module_doc_file = app.srcdir / "hardware/index.rst"

    title_str = textwrap.dedent("""

        .. _hardware-index:

        Hardware
        ========

        """)
    toc_list = ""
    with Path.open(module_doc_file, "w") as f:
        f.write(title_str)
        for vendor_module, vendor_module_info in doc_utils.iter_vendor_modules([hardware.__path__, core.__path__]):
            devices = doc_utils.extract_devices(vendor_module)
            if devices:
                try:
                    vendor_name = vendor_module.__vendor_name__
                except AttributeError:
                    vendor_name = vendor_module_info.name

                f.write(f".. collapsible:: {vendor_name}\n\n")
                if vendor_module.__doc__ is not None:
                    module_doc_str = parse(vendor_module.__doc__).long_description
                    if module_doc_str:
                        f.write(
                            pad_rst_content(
                                "\n".join(GoogleDocstring(module_doc_str, app.config, app, "module").lines()), 1
                            )
                        )
                        f.write(pad_rst_content("\n", 1))
                for device in devices:
                    basepath = f"generated/{vendor_module_info.name}/{device[0]}"
                    toc_list += f"{basepath}\n"

                    device_html = f"{basepath}.html"
                    f.write(pad_rst_content(build_device_link(device[0], device[1], device_html), 1))

                    device_page = app.srcdir / f"hardware/{basepath}.rst"
                    device_page.parent.mkdir(parents=True, exist_ok=True)
                    with Path.open(device_page, "w") as f_device:
                        if not DEVICE_TOC:
                            f_device.write(":orphan:\n\n")
                        f_device.write(build_device_page(app, vendor_module, vendor_name, *device))

        if DEVICE_TOC:
            f.write(
                textwrap.dedent("""
                All Devices
                -----------

                .. toctree::
                   :maxdepth: 3
                   :glob:

                """)
            )
            f.write(pad_rst_content(toc_list, 1))


def setup(app: "Sphinx") -> None:
    """Register hooks on sphinx start."""
    app.connect("builder-inited", build_hardware_pages)
