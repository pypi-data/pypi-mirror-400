"""A directive to create a collapsible section."""  # noqa: INP001

import uuid

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


class _HTMLInput(_HTMLTagElement):
    """Input HTML element."""

    _tagname = "input"
    _endtag = False


class _HTMLLabel(_HTMLTagElement):
    """Input HTML element."""

    _tagname = "label"
    _endtag = True


class CollapsibleDirective(SphinxDirective):
    """Build a collapsible box directive."""

    required_arguments = 1  # Title of the collapsible section
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        "badge": directives.unchanged,
        "badgetext": directives.unchanged,
        "summary": directives.unchanged,
        "open": directives.flag,
    }

    def run(self) -> list[nodes.container]:  # noqa: D102
        title = " ".join(self.arguments)
        self.assert_has_content()
        unique_id = str(uuid.uuid4())

        container = nodes.container("", is_div=True, classes=["accordion"])
        if "open" in self.options:
            inp = _HTMLInput(type="checkbox", name=f"collapse-{unique_id}", ids=[f"handle-{unique_id}"], checked=True)
        else:
            inp = _HTMLInput(type="checkbox", name=f"collapse-{unique_id}", ids=[f"handle-{unique_id}"])
        handle = nodes.container("", is_div=True, classes=["collapse-handle"])
        label = _HTMLLabel(**{"for": f"handle-{unique_id}"})
        label += nodes.Text(title)
        if "badge" in self.options:
            badge = nodes.container("", is_div=True, classes=["badge", self.options["badge"]])
            if "badgetext" in self.options:
                badge += nodes.Text(self.options["badgetext"])
            label.append(badge)
        if "summary" in self.options:
            summary = nodes.container("", is_div=True, classes=["collapse-summary"])
            summary += nodes.Text(self.options["summary"])
            label += summary

        handle += label
        content = nodes.container("", is_div=True, classes=["collapse-content"])
        self.state.nested_parse(self.content, self.content_offset, content)
        container += inp
        container += handle
        container += content
        return [container]


def setup(app: Sphinx) -> None:
    """Register HTML nodes and collapsible directive."""
    app.add_node(
        _HTMLLabel,
        html=(_HTMLLabel.visit, _HTMLLabel.depart),
        latex=(_HTMLLabel.default, _HTMLLabel.default),
    )
    app.add_node(
        _HTMLInput,
        html=(_HTMLInput.visit, _HTMLInput.depart),
        latex=(_HTMLLabel.default, _HTMLLabel.default),
    )
    app.add_directive("collapsible", CollapsibleDirective)
