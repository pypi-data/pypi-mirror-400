"""
sphinx_code_examples.directive
"""

from docutils.statemachine import ViewList

from typing import List
from docutils.nodes import Node

from sphinx.util.docutils import SphinxDirective
from docutils.parsers.rst import directives
from .nodes import (
    codex_node,
    codex_enumerable_node,
    codex_end_node,
    codex_title,
    codex_subtitle,
)
from docutils import nodes
from sphinx.util import logging

from sphinx.locale import get_translation

logger = logging.getLogger(__name__)

MESSAGE_CATALOG_NAME = "codex"
translate = get_translation(MESSAGE_CATALOG_NAME)



class SphinxCodexBaseDirective(SphinxDirective):
    def duplicate_labels(self, label):
        """Check for duplicate labels"""

        if label != "" and label in self.env.sphinx_codex_registry:
            docpath = self.env.doc2path(self.env.docname)
            path = docpath[: docpath.rfind(".")]
            other_path = self.env.doc2path(
                self.env.sphinx_codex_registry[label]["docname"]
            )
            msg = f"duplicate label: {label}; other instance in {other_path}"
            logger.warning(msg, location=path, color="red")
            return True

        return False


class CodexDirective(SphinxCodexBaseDirective):
    """
    A codex directive

    .. codex:: <subtitle> (optional)
       :label:
       :class:
       :nonumber:
       :hidden:

    Arguments
    ---------
    subtitle : str (optional)
            Specify a custom subtitle to add to the codex output

    Parameters:
    -----------
    label : str,
            A unique identifier for your codex that you can use to reference
            it with {ref} and {numref}
    class : str,
            Value of the codex’s class attribute which can be used to add custom CSS
    nonumber :  boolean (flag),
                Turns off codex auto numbering.
    hidden  :   boolean (flag),
                Removes the directive from the final output.
    """

    name = "codex"
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        "label": directives.unchanged_required,
        "class": directives.class_option,
        "nonumber": directives.flag,
        "hidden": directives.flag,
        "en": directives.unchanged,
        "zh-cn": directives.unchanged,
        "zh-tw": directives.unchanged,
        "hi": directives.unchanged,
        "es": directives.unchanged,
        "fr": directives.unchanged,
        "ar": directives.unchanged,
        "bn": directives.unchanged,
        "ru": directives.unchanged,
        "pt": directives.unchanged,
        "id": directives.unchanged,
        "ja": directives.unchanged,
        "de": directives.unchanged,
        "ko": directives.unchanged,
        "tr": directives.unchanged,
        "vi": directives.unchanged,
        "ta": directives.unchanged,
        "it": directives.unchanged,
        "th": directives.unchanged,
        "nl": directives.unchanged,
        "el": directives.unchanged,
        "pl": directives.unchanged,
        "uk": directives.unchanged,
        "fa": directives.unchanged,
        "ms": directives.unchanged,
        "sw": directives.unchanged,
        "ro": directives.unchanged,
        "cs": directives.unchanged,
        "hu": directives.unchanged,
        "he": directives.unchanged,
        "sv": directives.unchanged,
        "no": directives.unchanged,
    }

    def run(self) -> List[Node]:
        self.defaults = {"title_text": translate(self.env.config.sphinx_codex_name)}
        self.serial_number = self.env.new_serialno()

        # Initialise Registry (if needed)
        if not hasattr(self.env, "sphinx_codex_registry"):
            self.env.sphinx_codex_registry = {}

        # Construct Title
        title = codex_title()
        title += nodes.Text(self.defaults["title_text"])

        # Select Node Type and Initialise
        if "nonumber" in self.options:
            node = codex_node()
        else:
            node = codex_enumerable_node()

        if self.name == "codex-start":
            node.gated = True

        # Parse custom subtitle option
        if self.arguments != []:
            subtitle = codex_subtitle()
            subtitle_text = f"{self.arguments[0]}"
            subtitle_nodes, _ = self.state.inline_text(subtitle_text, self.lineno)
            for subtitle_node in subtitle_nodes:
                subtitle += subtitle_node
            title += subtitle

        # add the stuff for the visual if given in the set language
        # get lang of document
        lang = self.env.config.language
        # see if lang is a given option
        result = self.options.get(lang, None)
        if result is not None:
            # a value has been given, so add it to the example
            new_content = ViewList()
            new_content.append('<div class="example-info" style="display: block;"></div>', "<generated>", 0)
            new_content.append("", "<generated>", 0)
            new_content.append('<div class="example-text" style="display: block;">', "<generated>", 0)
            new_content.extend(self.content)   # add original content after new_content
            new_content.append('</div>', "<generated>", 0)
            new_content.append("", "<generated>", 0)
            new_content.append(f'```{{video}} {result}',"<generated>",0)
            new_content.append(':divclass: example-animation',"<generated>",0)
            new_content.append(':stylediv: "display: none;"',"<generated>",0)
            new_content.append(':width: 100%',"<generated>",0)
            new_content.append(':aspectratio: auto 16/9',"<generated>",0)
            new_content.append('```',"<generated>",0)
            self.content = new_content

        # State Parsing
        section = nodes.section(ids=["codex-content"])
        self.state.nested_parse(self.content, self.content_offset, section)

        # Construct a label
        label = self.options.get("label", "")
        if label:
            # TODO: Check how :noindex: is used here
            self.options["noindex"] = False
        else:
            self.options["noindex"] = True
            label = f"{self.env.docname}-codex-{self.serial_number}"

        # Check for Duplicate Labels
        # TODO: Should we just issue a warning rather than skip content?
        if self.duplicate_labels(label):
            return []

        # Collect Classes
        if self.env.config.sphinx_codex_style_from_proof:
            if self.env.config.sphinx_codex_icon_from_proof:
                classes = [f"proof example"]
            else:
                classes = [f"proof example {self.name}"]
        else:
            classes = [f"{self.name}"]
        if self.options.get("class"):
            classes.extend(self.options.get("class"))
        if result is not None:
            classes.append("dual")

        self.options["name"] = label

        # Construct Node
        node += title
        node += section
        node["classes"].extend(classes)
        node["ids"].append(label)
        node["label"] = label
        node["docname"] = self.env.docname
        node["title"] = self.defaults["title_text"]
        node["type"] = self.name
        node["hidden"] = True if "hidden" in self.options else False
        node["serial_number"] = self.serial_number
        node.document = self.state.document

        self.add_name(node)
        self.env.sphinx_codex_registry[label] = {
            "type": self.name,
            "docname": self.env.docname,
            # Copy the node so that the post transforms do not modify this original state
            # Prior to Sphinx 6.1.0, the doctree was not cached, and Sphinx loaded a new copy
            # c.f. https://github.com/sphinx-doc/sphinx/commit/463a69664c2b7f51562eb9d15597987e6e6784cd
            "node": node.deepcopy(),
        }

        # TODO: Could tag this as Hidden to prevent the cell showing
        # rather than removing content
        # https://github.com/executablebooks/sphinx-jupyterbook-latex/blob/8401a27417d8c2dadf0365635bd79d89fdb86550/sphinx_jupyterbook_latex/transforms.py#L108
        if node.get("hidden", bool):
            return []
        
        return [node]


# Gated Directives


class CodexStartDirective(CodexDirective):
    """
    A gated directive for codexs

    .. codex:: <subtitle> (optional)
       :label:
       :class:
       :nonumber:
       :hidden:

    This class is a child of CodexDirective so it supports
    all the same options as the base codex node
    """

    name = "codex-start"

    def run(self):
        # Initialise Gated Registry
        if not hasattr(self.env, "sphinx_codex_gated_registry"):
            self.env.sphinx_codex_gated_registry = {}
        gated_registry = self.env.sphinx_codex_gated_registry
        docname = self.env.docname
        if docname not in gated_registry:
            gated_registry[docname] = {
                "start": [],
                "end": [],
                "sequence": [],
                "msg": [],
                "type": "codex",
            }
        gated_registry[self.env.docname]["start"].append(self.lineno)
        gated_registry[self.env.docname]["sequence"].append("S")
        gated_registry[self.env.docname]["msg"].append(
            f"{self.name} at line: {self.lineno}"
        )
        # Run Parent Methods
        return super().run()


class CodexEndDirective(SphinxDirective):
    """
    A simple gated directive to mark end of an codex

    .. codex-end::
    """

    name = "codex-end"

    def run(self):
        # Initialise Gated Registry
        if not hasattr(self.env, "sphinx_codex_gated_registry"):
            self.env.sphinx_codex_gated_registry = {}
        gated_registry = self.env.sphinx_codex_gated_registry
        docname = self.env.docname
        if docname not in gated_registry:
            gated_registry[docname] = {
                "start": [],
                "end": [],
                "sequence": [],
                "msg": [],
                "type": "codex",
            }
        gated_registry[self.env.docname]["end"].append(self.lineno)
        gated_registry[self.env.docname]["sequence"].append("E")
        gated_registry[self.env.docname]["msg"].append(
            f"{self.name} at line: {self.lineno}"
        )
        return [codex_end_node()]

