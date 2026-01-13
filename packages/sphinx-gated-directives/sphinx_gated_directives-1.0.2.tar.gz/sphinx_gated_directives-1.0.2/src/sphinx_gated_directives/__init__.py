"""
~~~~~~~~~~~~~~~~~~~~

sphinx_gated_directives

~~~~~~~~~~~~~~~~~~~~

This package is an extension for Sphinx that creates a '-start' companion
and a '-end' companion for every registered class-based directive.

These new directives can be used to "gate" content in the documentation,
similar to how the gated directives of sphinx-exercise work.

This extension is based on the extension executablebooks/sphinx-exercise:
https://github.com/executablebooks/sphinx-exercise

Original project licensed under MIT © Executable Books Developers.
See the repository LICENSE for details.

Our implementation reuses certain ideas and code snippets (e.g., Docutils
compatibility helpers) to fit the needs of this extension.

"""

from __future__ import annotations
from docutils.nodes import Element
from typing import Iterator
import copy
import importlib
import inspect
from typing import Dict, Iterable, Optional
from sphinx.transforms import SphinxTransform
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment

from sphinx.util import logging
logger = logging.getLogger(__name__)

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives as du_directives

from dataclasses import dataclass, field

SUFFIX_START = "start"
SUFFIX_END = "end"
SUFFIX_SEPARATOR = "-"

def _is_class_directive(obj) -> bool:
    return inspect.isclass(obj) and issubclass(obj, Directive)

def _get_unified_registry(app=None) -> Dict[str, object]:
    # 1) Already-loaded directives (includes Sphinx & extensions registered via add_directive)
    unified: Dict[str, object] = dict(getattr(du_directives, "_directives", {}))

    # 2) Ensure Docutils built-ins are present by importing from _directive_registry
    reg = getattr(du_directives, "_directive_registry", {})
    for name, (modname, clsname) in reg.items():
        if name in unified:
            continue
        try:
            mod = importlib.import_module(f"docutils.parsers.rst.directives.{modname}")
            obj = getattr(mod, clsname, None)
            if obj is not None:
                unified[name] = obj
        except Exception:
            # Be defensive: if an import fails, just skip that name
            continue

    # 3) Add Sphinx's registry if app is provided
    if app is not None:
        # Sphinx stores directives in app.registry
        # Try different ways to access the directives mapping
        if hasattr(app.registry, 'directives'):
            # Newer Sphinx versions may have a directives attribute
            try:
                unified.update(app.registry.directives)
            except (AttributeError, TypeError):
                pass
        
        # Also check for domains which contain directives (e.g., prf:theorem from sphinx-proof)
        if hasattr(app.registry, 'domains'):
            for domain_name, domain_cls in app.registry.domains.items():
                try:
                    # Instantiate domain or use class attributes
                    if hasattr(domain_cls, 'directives'):
                        domain_directives = domain_cls.directives
                        for dir_name, dir_impl in domain_directives.items():
                            # Fully qualified name: domain:directive
                            full_name = f"{domain_name}:{dir_name}"
                            if full_name not in unified:
                                unified[full_name] = dir_impl
                except Exception:
                    continue

    return unified

def _copy_option_spec(option_spec):
    return copy.copy(option_spec) if isinstance(option_spec, dict) else option_spec

def make_start_class(orig_name: str, base_cls: type[Directive]) -> type[Directive]:
    
    attrs = {}
    for attr in (
        "required_arguments",
        "optional_arguments",
        "final_argument_whitespace",
        "has_content",
        "option_spec",
    ):
        if hasattr(base_cls, attr):
            val = getattr(base_cls, attr)
            if attr == "option_spec":
                attrs[attr] = _copy_option_spec(val) or {}
            else:
                attrs[attr] = val

    def run(self: Directive):
        current_name = self.name
        self.name = orig_name  # temporarily set to original for base run()
        children = base_cls.run(self)
        self.name = current_name  # restore
        if not isinstance(children, list):
            if isinstance(children, Iterable):
                children = list(children)
            else:
                children = [children]
        # create a start_node and add all result nodes as its children
        start_node_instance = start_node()
        start_node_instance += children
        result = [start_node_instance]

        # Get environment from state.document.settings
        env = getattr(self.state.document.settings, "env", None)
        if env is not None:
            docname = env.docname
            # 1) Check whether super registry has been created, if not, create it
            if not hasattr(env, "sphinx_gated_directives_registry"):
                env.sphinx_gated_directives_registry = {}
            # 2) Register current usage in the super registry
            registry = env.sphinx_gated_directives_registry
            if docname not in registry:
                registry[docname] = {
                    "start": [],
                    "end": [],
                    "sequence": [],
                    "msg": [],
                    "type": [],
                }
            registry[docname]["start"].append(self.lineno)
            registry[docname]["sequence"].append("S")
            registry[docname]["msg"].append(
                f"{self.name} at line: {self.lineno}"
            )
            registry[docname]["type"].append(orig_name)

        return result

    attrs["run"] = run
    new_cls_name = f"{base_cls.__name__}_Start_For_{orig_name.replace(':', '_')}"
    return type(new_cls_name, (base_cls,), attrs)

def make_end_class(orig_name: str, base_cls: type[Directive]) -> type[Directive]:

    attrs = {}
    for attr in (
        "required_arguments",
        "optional_arguments",
        "final_argument_whitespace",
        "has_content",
        "option_spec",
    ):
        if hasattr(base_cls, attr):
            val = getattr(base_cls, attr)
            if attr == "option_spec":
                attrs[attr] = _copy_option_spec(val) or {}
            else:
                attrs[attr] = val

    def run(self: Directive):

        # Get environment from state.document.settings
        env = getattr(self.state.document.settings, "env", None)
        if env is not None:
            docname = env.docname
            # 1) Check whether super registry has been created, if not, create it
            if not hasattr(env, "sphinx_gated_directives_registry"):
                env.sphinx_gated_directives_registry = {}
            # 2) Register current usage in the super registry
            registry = env.sphinx_gated_directives_registry
            if docname not in registry:
                registry[docname] = {
                    "start": [],
                    "end": [],
                    "sequence": [],
                    "msg": [],
                    "type": [],
                }
            registry[docname]["end"].append(self.lineno)
            registry[docname]["sequence"].append("E")
            registry[docname]["msg"].append(
                f"{self.name} at line: {self.lineno}"
            )
            registry[docname]["type"].append(orig_name)

        return [end_node()]

    attrs["run"] = run
    new_cls_name = f"{base_cls.__name__}_End_For_{orig_name.replace(':', '_')}"
    return type(new_cls_name, (base_cls,), attrs)

def _should_skip_name(orig_name: str, cfg: dict) -> bool:
    suffix_separator = cfg["suffix_separator"]
    suffix_start = cfg["suffix_start"]
    suffix_end = cfg["suffix_end"]
    if isinstance(cfg["override_existing"],bool):
        if cfg["override_existing"] is True:
            return False
        else:
            if orig_name.endswith(f"{suffix_separator}{suffix_start}"):
                return True
            else:
                return orig_name.endswith(f"{suffix_separator}{suffix_end}")
    elif isinstance(cfg["override_existing"],list):
        if orig_name in cfg["override_existing"]:
            return False
        else:
            if orig_name.endswith(f"{suffix_separator}{suffix_start}"):
                return True
            else:
                return orig_name.endswith(f"{suffix_separator}{suffix_end}")

def _register_new_directives(app, env, docnames):

    # get options and add missing default values
    cfg = app.config.sphinx_gated_directives
    if "override_existing" not in cfg:
        cfg["override_existing"] = False
    elif isinstance(cfg["override_existing"], str):
        cfg["override_existing"] = [cfg["override_existing"]]
    if "suffix_start" not in cfg:
        cfg["suffix_start"] = SUFFIX_START
    if "suffix_end" not in cfg:
        cfg["suffix_end"] = SUFFIX_END
    if "suffix_separator" not in cfg:
        cfg["suffix_separator"] = SUFFIX_SEPARATOR

    unified = _get_unified_registry(app)
    snapshot_names = set(unified.keys())
    added = 0

    suffix_separator = cfg["suffix_separator"]
    suffix_start = cfg["suffix_start"]
    suffix_end = cfg["suffix_end"]
    for orig_name, obj in sorted(unified.items()):

        new_name = f"{orig_name}{suffix_separator}{suffix_start}"
        # add start and end directives if not already present, or if override is requested explicitly
        if new_name in snapshot_names:
            if isinstance(cfg["override_existing"], bool):
                if cfg["override_existing"] is False:
                    continue
            else:
                if orig_name not in cfg["override_existing"]:
                    continue
        end_name = f"{orig_name}{suffix_separator}{suffix_end}"
        if end_name in snapshot_names:
            if isinstance(cfg["override_existing"], bool):
                if cfg["override_existing"] is False:
                    continue
            else:
                if orig_name not in cfg["override_existing"]:
                    continue

        # if the original name is itself a start or end directive, skip
        if _should_skip_name(orig_name,cfg):
            continue

        try:
            if _is_class_directive(obj):
                start_cls = make_start_class(orig_name, obj) # new class based on original so all properties are inherited
                app.add_directive(new_name, start_cls,override=True)
                end_cls = make_end_class(orig_name, Directive) # because it does not generate anything, most simple directive possible
                app.add_directive(end_name, end_cls,override=True)
                added += 1
            else:
                logger.debug(f"[sphinx-gated-directives] '{orig_name}' is not a class directive; skipping.")
        except Exception as e:
            logger.warning(f"[sphinx-gated-directives] failed to register new classes for directive '{orig_name}':\n{e}")

def setup(app):
    # Register a config value to set options for the extension
    app.add_config_value("sphinx_gated_directives", {}, "env")

    # Register a function to check if config value structure is correct
    app.connect("config-inited", check_config_values)

    # register function to purge registries at start of build per document
    app.connect("env-purge-doc", purge_registries)
    
    # At the latest possible moment, register new directives
    app.connect("env-before-read-docs", _register_new_directives,priority=10000000000000000000000000000)

    # Register nodes
    # During transformation phase, these nodes will be removed
    app.add_node(start_node)
    app.add_node(end_node)

    # Register a transform to check validity of start-end pairs
    app.add_transform(CheckGatedDirectivesTransform)

    # Register a transform to merge start-end pairs into gated content
    app.add_transform(MergeGatedDirectivesTransform)

    return {
        "parallel_read_safe": True,
    }

class start_node(nodes.Admonition, nodes.Element):
    pass

class end_node(nodes.Admonition, nodes.Element):
    pass

def purge_registries(app: Sphinx, env: BuildEnvironment, docname: str) -> None:

    if hasattr(env, "sphinx_gated_directives_registry"):
        registry = env.sphinx_gated_directives_registry
        if docname in registry:
            del registry[docname]

# Transform to check validity of start-end pairs
class CheckGatedDirectivesTransform(SphinxTransform):
    default_priority = 1

    def apply(self, **kwargs):
        env = self.env
        if not hasattr(env, "sphinx_gated_directives_registry"):
            return
        
        registry = env.sphinx_gated_directives_registry
        error = False
        docname = self.env.docname
        if docname in registry:
            start = registry[docname]["start"]
            end = registry[docname]["end"]
            structure = "\n  ".join(registry[docname]["msg"])
            sequence = "".join(registry[docname]["sequence"])
            validate_SE_result = validate_SE(sequence)
            if len(start) > len(end):
                msg = f"[sphinx-gated-directives] The document {docname} contains more start directives than end directives:\n  {structure}\nPlease ensure each start directive has a corresponding end directive."
                logger.error(msg)
                error = True
            elif len(end) > len(start):
                msg = f"[sphinx-gated-directives] The document {docname} contains more end directives than start directives:\n  {structure}\nPlease ensure each end directive has a corresponding start directive."
                logger.error(msg)
                error = True
            # at this point, len(start) == len(end)
            # now check for correct nesting
            elif not validate_SE_result.is_valid:
                msg = f"[sphinx-gated-directives] The document {docname} contains incorrectly nested start and end directives:\n  {structure}\nThis is not allowed. Please correct the nesting."
                logger.error(msg)
                error = True
            else:
                # At this point, every start is matched with an end
                # Now check that types match in order.
                types = registry[docname]["type"]
                start_type = [types[k] for k in validate_SE_result.pairs.keys()]
                end_type = [types[v] for v in validate_SE_result.pairs.values()]
                for i in range(len(start_type)):
                    if start_type[i] != end_type[i]:
                        msg = f"[sphinx-gated-directives] The document {docname} contains mismatched start and end directives at lines {start[i]} and {end[i]}:\n  {structure}\nPlease ensure that start and end directives match in type."
                        logger.error(msg)
                        error = True
                        break

        if error:
            raise Exception(f"[sphinx-gated-directives] An error has occurred when parsing gated directives in {docname}.\nPlease check warning messages above.")
        
class MergeGatedDirectivesTransform(SphinxTransform):
    default_priority = 10

    def apply(self, **kwargs):
        env = self.env
        if not hasattr(env, "sphinx_gated_directives_registry"):
            return
        registry = env.sphinx_gated_directives_registry
        docname = self.env.docname
        if docname not in registry:
            return
        
        start_nodes = findall(self.document, start_node)
        for start_n in start_nodes:
            parent = start_n.parent
            found_start = False
            end_n = None
            skip_end = 0
            for child in parent.children:
                if child is start_n:
                    found_start = True
                elif found_start and isinstance(child, end_node) and skip_end==0:
                    end_n = child
                    break
                elif found_start and isinstance(child, end_node):
                    skip_end -= 1
                elif found_start and isinstance(child, start_node):
                    skip_end += 1
            if end_n is None:
                logger.error(f"[sphinx-gated-directives] Could not find matching end directive for start directive at line {start_n.line} in document {docname}. Skipping merging for this pair.")
                raise Exception(f"[sphinx-gated-directives] An error has occurred when parsing gated directives in {docname}.\nPlease check warning messages above.")

            start_index = parent.children.index(start_n)
            end_index = parent.children.index(end_n)
            between_nodes = parent.children[start_index + 1:end_index]

            new_nodes = start_n.children
            if between_nodes:
                has_section = False
                has_caption = False
                si = -1
                content = new_nodes[-1]
                for sn in content.children:
                    si += 1
                    if isinstance(sn, nodes.section):
                        has_section = True
                        section_index = si
                        section_node = sn
                        break
                    elif isinstance(sn, nodes.caption):
                        has_caption = True
                        caption_index = si
                        caption_node = sn
                        break
                if has_section:
                    content[section_index] += between_nodes
                elif has_caption:
                    n = len(content.children)
                    pos = n - 1
                    for i, bn in enumerate(between_nodes):
                            content.insert(pos + i, bn)
                else:
                    for bn in between_nodes:
                        content += bn
                    
            start_pos = parent.children.index(start_n)
            parent.remove(end_n)
            parent.remove(start_n)
            for bn in between_nodes:
                parent.remove(bn)
            for i, nn in enumerate(new_nodes):
                parent.insert(start_pos + i, nn)


# SPDX-License-Identifier: MIT
# Adapted from: executablebooks/sphinx-exercise, file: sphinx_exercise/_compat.py
# Source: https://github.com/executablebooks/sphinx-exercise/blob/main/sphinx_exercise/_compat.py
# License: MIT — © Executable Books Developers (see repository LICENSE).
def findall(node: Element, *args, **kwargs) -> Iterator[Element]:
    # findall replaces traverse in docutils v0.18
    # note a difference is that findall is an iterator
    impl = getattr(node, "findall", node.traverse)
    return iter(impl(*args, **kwargs))

@dataclass
class SEValidationResult:
    is_valid: bool
    pairs: Dict[int, int] = field(default_factory=dict)  # {S_index: E_index}
    error_index: Optional[int] = None                   # index of first error, if any
    error_message: Optional[str] = None                 # description of the error, if any

def validate_SE(s: str) -> SEValidationResult:
    stack = []
    pairs: Dict[int, int] = {}

    for i, ch in enumerate(s):
        if ch == 'S':
            stack.append(i)
        elif ch == 'E':
            if not stack:
                return SEValidationResult(
                    is_valid=False,
                    pairs=pairs,
                    error_index=i,
                    error_message="Encountered 'E' before a matching 'S'."
                )
            s_index = stack.pop()
            pairs[s_index] = i
        else:
            return SEValidationResult(
                is_valid=False,
                pairs=pairs,
                error_index=i,
                error_message=f"Invalid character: {ch!r}. Only 'S' and 'E' are allowed."
            )

    if stack:
        return SEValidationResult(
            is_valid=False,
            pairs=pairs,
            error_index=len(s),
            error_message=f"{len(stack)} unmatched 'S' remaining at end."
        )

    return SEValidationResult(is_valid=True, pairs=pairs)

def check_config_values(app: Sphinx, config) -> None:
    cfg = config.sphinx_gated_directives
    if not isinstance(cfg, dict):
        logger.error("[sphinx-gated-directives] The configuration value 'sphinx_gated_directives' should be a dictionary.")
        raise ValueError("Invalid configuration for 'sphinx_gated_directives'. Expected a dictionary.")
        return
    # Implemented options:
    # - override_existing: bool (default: False), string or list of strings
    override_existing = cfg.get("override_existing", False)
    if not (isinstance(override_existing, bool) or isinstance(override_existing, str) or (isinstance(override_existing, list) and all(isinstance(x, str) for x in override_existing))):
        logger.error("[sphinx-gated-directives] The configuration option 'override_existing' should be a boolean, a string, or a list of strings.")
        raise ValueError("Invalid configuration for 'sphinx_gated_directives.override_existing'. Expected a boolean, string, or list of strings.")
    # - suffix_start: string (default: 'start'), only a-z allowed, or empty string
    suffix_start = cfg.get("suffix_start", SUFFIX_START)
    if not isinstance(suffix_start, str):
        logger.error("[sphinx-gated-directives] The configuration option 'suffix_start' should be a string.")
        raise ValueError("Invalid configuration for 'sphinx_gated_directives.suffix_start'. Expected a string.")
    if suffix_start != "" and (not suffix_start.islower() or not suffix_start.isalpha()):
        logger.error("[sphinx-gated-directives] The configuration option 'suffix_start' should contain only lowercase letters (a-z).")
        raise ValueError("Invalid configuration for 'sphinx_gated_directives.suffix_start'. Expected only lowercase letters (a-z).")
    # - suffix_end: string (default: 'end'), only a-z allowed, or empty string
    suffix_end = cfg.get("suffix_end", SUFFIX_END)
    if not isinstance(suffix_end, str):
        logger.error("[sphinx-gated-directives] The configuration option 'suffix_end' should be a string.")
        raise ValueError("Invalid configuration for 'sphinx_gated_directives.suffix_end'. Expected a string.")
    if suffix_end != "" and (not suffix_end.islower() or not suffix_end.isalpha()):
        logger.error("[sphinx-gated-directives] The configuration option 'suffix_end' should contain only lowercase letters (a-z).")
        raise ValueError("Invalid configuration for 'sphinx_gated_directives.suffix_end'. Expected only lowercase letters (a-z).")
    # - suffix_separator: string (default: '-'), single character, no space, no underscore, no colon, or empty string
    suffix_separator = cfg.get("suffix_separator", SUFFIX_SEPARATOR)
    if not isinstance(suffix_separator, str):
        logger.error("[sphinx-gated-directives] The configuration option 'suffix_separator' should be a string.")
        raise ValueError("Invalid configuration for 'sphinx_gated_directives.suffix_separator'. Expected a string.")
    if len(suffix_separator) > 1:
        logger.error("[sphinx-gated-directives] The configuration option 'suffix_separator' should be a single character or an empty string.")
        raise ValueError("Invalid configuration for 'sphinx_gated_directives.suffix_separator'. Expected a single character or an empty string.")
    if suffix_separator in [' ', '_',':']:
        logger.error("[sphinx-gated-directives] The configuration option 'suffix_separator' should not be a space, nor an underscore, nor a colon.")
        raise ValueError("Invalid configuration for 'sphinx_gated_directives.suffix_separator'. Expected something other than a space, an underscore, or a colon.")
    