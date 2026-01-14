"""A directive to create a collapsible section."""  # noqa: INP001

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective


class _HTMLTagElement(nodes.Element, nodes.General):
    """Adapted from https://github.com/pradyunsg/sphinx-inline-tabs."""

    @staticmethod
    def visit(translator, node):  # noqa: ANN001, ANN205
        attributes = node.attributes.copy()
        # Nobody needs this crap.
        attributes.pop("ids")
        attributes.pop("classes")
        attributes.pop("names")
        attributes.pop("dupnames")
        attributes.pop("backrefs")

        if node._endtag:
            text = translator.starttag(node, node._tagname, **attributes)
        else:
            text = translator.emptytag(node, node._tagname, **attributes)

        translator.body.append(text.strip())

    @staticmethod
    def depart(translator, node):  # noqa: ANN001, ANN205
        if node._endtag:
            translator.body.append(f"</{node._tagname}>")

    @staticmethod
    def default(translator, node):  # noqa: ANN001, ANN205
        pass


class _HTMLAnchor(_HTMLTagElement):
    """Input HTML element."""

    _tagname = "a"
    _endtag = True


class DriverboxDirective(SphinxDirective):
    """Build a collapsible box directive."""

    required_arguments = 1  # Title of the collapsible section
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False
    option_spec = {
        "badge": directives.unchanged,
        "badgetext": directives.unchanged,
        "summary": directives.unchanged,
        "ref": directives.unchanged,
        "open": directives.flag,
    }

    def run(self) -> list[nodes.Element]:  # noqa: D102
        title = " ".join(self.arguments)

        container = nodes.container("", is_div=True, classes=["driverbox"])
        container += nodes.strong(title, title)
        if "badge" in self.options:
            badge = nodes.container("", is_div=True, classes=["badge", self.options["badge"]])
            if "badgetext" in self.options:
                badge += nodes.Text(self.options["badgetext"])
            container += badge
        if "summary" in self.options:
            summary = nodes.container("", is_div=True, classes=["summary"])
            summary += nodes.Text(self.options["summary"])
            container += summary

        if "ref" in self.options:
            ref = _HTMLAnchor(href=self.options["ref"], classes=["no-decoration"])
            ref += container
            return [ref]
        return [container]


def setup(app: Sphinx) -> None:
    """Register HTML nodes and driverbox directive."""
    app.add_node(
        _HTMLAnchor,
        html=(_HTMLAnchor.visit, _HTMLAnchor.depart),
        latex=(_HTMLAnchor.default, _HTMLAnchor.default),
    )
    app.add_directive("driverbox", DriverboxDirective)
