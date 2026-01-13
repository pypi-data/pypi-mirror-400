from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Callable, Generic, Iterable, List, Optional, Sequence, TypeVar

T = TypeVar("T")  # Generic type variable for items
V = TypeVar("V")  # Generic type variable for attribute values


# =========================
# 1. Specification (predicate)
# =========================


class Specification(Generic[T]):
    """
    A composable predicate object:
    - spec(item) -> bool
    - supports spec1 & spec2, spec1 | spec2, ~spec1
    """

    def __init__(self, predicate: Callable[[T], bool]):
        self._predicate = predicate

    def __call__(self, item: T) -> bool:
        return self._predicate(item)

    # AND
    def __and__(self, other: Specification[T]) -> Specification[T]:
        return Specification(lambda item: self(item) and other(item))

    # OR
    def __or__(self, other: Specification[T]) -> Specification[T]:
        return Specification(lambda item: self(item) or other(item))

    # NOT
    def __invert__(self) -> Specification[T]:
        return Specification(lambda item: not self(item))

    # Common static constructors
    @staticmethod
    def always_true() -> Specification[T]:
        return Specification(lambda _: True)

    @staticmethod
    def always_false() -> Specification[T]:
        return Specification(lambda _: False)


# Attribute-level helper (works with any item type as long as getter is valid)
def attr_spec(
    getter: Callable[[T], V],
    value_predicate: Callable[[V], bool],
) -> Specification[T]:
    """Lift an attribute predicate into a Specification over the whole item."""

    return Specification(lambda item: value_predicate(getter(item)))


# =========================
# 2. Transformer (transformation strategy)
# =========================


class Transformer(Generic[T]):
    """
    Transform an item:
    - transformer(item) -> new_item
    - supports composition: t1.then(t2)
    """

    def __init__(self, func: Callable[[T], T]):
        self._func = func

    def __call__(self, item: T) -> T:
        return self._func(item)

    def then(self, other: Transformer[T]) -> Transformer[T]:
        """Apply this transformer first, then apply `other`."""

        return Transformer(lambda item: other(self(item)))

    @staticmethod
    def identity() -> Transformer[T]:
        return Transformer(lambda item: item)


def attr_transform(
    getter: Callable[[T], V],
    setter: Callable[[T, V], T],
    value_func: Callable[[V], V],
) -> Transformer[T]:
    """
    Transform a single attribute: new_value = value_func(old_value)

    Note: this makes no assumption about the item type; any getter/setter pair works.
    """

    def _inner(item: T) -> T:
        old_value = getter(item)
        new_value = value_func(old_value)
        return setter(item, new_value)

    return Transformer(_inner)


# Common setter helpers (dict / dataclass)
def dict_setter(key: str) -> Callable[[dict, V], dict]:
    def _setter(item: dict, value: V) -> dict:
        new_item = dict(item)
        new_item[key] = value
        return new_item

    return _setter


def dataclass_setter(field_name: str) -> Callable[[T, V], T]:
    def _setter(item: T, value: V) -> T:
        if not is_dataclass(item):
            raise TypeError("dataclass_setter only works with dataclass instances")
        return replace(item, **{field_name: value})

    return _setter


# =========================
# 3. Rule: condition + transformation
# =========================


class Rule(Generic[T]):
    """
    A rule = trigger condition (Specification) + transformation (Transformer) applied on match.

    - if condition returns True, the rule is considered "matched"
    - if transform is None, the item is returned unchanged
    """

    def __init__(
        self,
        condition: Specification[T],
        transform: Optional[Transformer[T]] = None,
        name: Optional[str] = None,
        stop_on_match: bool = False,
    ):
        self.condition = condition
        self.transform = transform or Transformer.identity()
        self.name = name or "<unnamed-rule>"
        self.stop_on_match = stop_on_match

    def matches(self, item: T) -> bool:
        return self.condition(item)

    def apply(self, item: T) -> T:
        return self.transform(item)


# =========================
# 4. RuleEngine: apply rules to items
# =========================


class RuleEngine(Generic[T]):
    """
    Core rule engine (business-agnostic):

    - supports multiple rules
    - controls whether unmatched items are kept
    - controls matching mode across rules (all / first)
    """

    def __init__(
        self,
        rules: Sequence[Rule[T]],
        *,
        keep_unmatched: bool = False,
        match_mode: str = "all",  # "all" or "first"
    ):
        if match_mode not in ("all", "first"):
            raise ValueError("match_mode must be 'all' or 'first'")
        self.rules: List[Rule[T]] = list(rules)
        self.keep_unmatched = keep_unmatched
        self.match_mode = match_mode

    def process(self, items: Iterable[T]) -> List[T]:
        """
        Accept any iterable of items and return a new list of items.
        """

        result: List[T] = []

        for original in items:
            item = original
            matched_any = False

            for rule in self.rules:
                if not rule.matches(item):
                    continue

                matched_any = True
                item = rule.apply(item)

                if self.match_mode == "first" or rule.stop_on_match:
                    break

            if matched_any or self.keep_unmatched:
                result.append(item)

        return result


