from dataclasses import dataclass
from typing import Union, Tuple, TypeVar


@dataclass(frozen=True)
class ValueOfType:
    """
    Represents a fact argument of a particular type.

    Used in `Oso.get` and `Oso.delete` to fetch and delete facts with an argument of the given type.
    See the documentation for those functions for more information.
    """

    type: str


@dataclass(frozen=True)
class Value:
    """
    An argument to a fact, with a type and an id.
    """

    type: str
    id: str


T = TypeVar("T")
_FactShaped = Union[
    Tuple[str, T],
    Tuple[str, T, T],
    Tuple[str, T, T, T],
    Tuple[str, T, T, T, T],
    Tuple[str, T, T, T, T, T],
]

Fact = _FactShaped[Value]
"""
A tuple of a string predicate and a series of Value arguments.

Facts are the core data model of Oso Cloud.
See also: https://www.osohq.com/docs/concepts/oso-cloud-data-model

### Example
```python
user = Value("User", "1")
role = Value("String", "admin")
org = Value("Organization", "2")
user_admin: Fact = ("has_role", user, role, org)
```
"""

IntoValue = Union[bool, str, int, Value]
"""
A type that can be coerced into a Value.
"""

IntoFact = _FactShaped[IntoValue]
"""
A type that can be coerced into a Fact.
### Example
```python
user = Value("User", "1")
role ="admin"
org = Value("Organization", "2")
user_admin: IntoFact = ("has_role", user, role, org)
```
"""


IntoValuePattern = Union[IntoValue, ValueOfType, None]
IntoFactPattern = _FactShaped[IntoValuePattern]
"""
A pattern for `Oso.get` or `Oso.delete`.

A predicate and a series of arguments, some of which may be `None`
(representing a total wildcard) or `ValueOfType` in addition to fixed `Value`s.
"""


@dataclass(frozen=True)
class ExpectedResult:
    request_id: str
    expected: bool
