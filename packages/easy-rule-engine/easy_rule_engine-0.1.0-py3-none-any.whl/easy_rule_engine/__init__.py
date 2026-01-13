"""
easy-rule-engine

Public API re-exports.
"""

from .core import (
    Rule,
    RuleEngine,
    Specification,
    Transformer,
    attr_spec,
    attr_transform,
    dataclass_setter,
    dict_setter,
)

__all__ = [
    "Specification",
    "Transformer",
    "Rule",
    "RuleEngine",
    "attr_spec",
    "attr_transform",
    "dict_setter",
    "dataclass_setter",
]


