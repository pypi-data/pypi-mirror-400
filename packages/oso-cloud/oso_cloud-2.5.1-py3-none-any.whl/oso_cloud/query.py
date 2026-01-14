import collections
import dataclasses
import random
import string
from typing import (
    Any,
    Dict,
    List,
    NewType,
    Optional,
    overload,
    Sequence,
    Tuple,
    TYPE_CHECKING,
    Union,
)
from typing_extensions import Self

from .helpers import to_api_facts, to_api_value
from . import api, types
from .api import OsoException

# We need `Oso` only for the type hints, but importing it directly causes
# a cyclic import (`oso.py` imports `query.py` imports `oso.py`).
# This conditional avoids this issue.
if TYPE_CHECKING:
    from . import Oso


QueryId = NewType("QueryId", str)


@dataclasses.dataclass
class ApiQueryCall:
    predicate: str
    args: List[QueryId]


@dataclasses.dataclass
class QueryConstraint:
    type: str
    ids: Optional[List[str]]

    def clone(self):
        ids = None if self.ids is None else list(self.ids)
        return dataclasses.replace(self, ids=ids)


def _random_id() -> QueryId:
    entropy = "".join(random.choices(string.ascii_lowercase + string.digits, k=7))
    return QueryId(f"var_{entropy}")


@dataclasses.dataclass(frozen=True)
class QueryVariable:
    type: str
    id: QueryId = dataclasses.field(default_factory=_random_id, init=False)


Value = Union[QueryVariable, types.IntoValue]
QueryArgs = Union[
    Tuple[str, Value],
    Tuple[str, Value, Value],
    Tuple[str, Value, Value, Value],
    Tuple[str, Value, Value, Value, Value],
    Tuple[str, Value, Value, Value, Value, Value],
]

EvaluateArgItem = Union[
    QueryVariable,
    Tuple["EvaluateArgItem", ...],
]
EvaluateArg = Union[
    None,
    EvaluateArgItem,
    Dict[QueryVariable, "EvaluateArg"],
]


def typed_var(type: str) -> QueryVariable:
    """Construct a new query variable of a specific type.
    @param type The actor/resource type of the variable to be created.
      Note: This must NOT be the "Actor" or "Resource" abstract types.
      To query for many types of results, make one request for each concrete
      type.
    @returns A new variable that can be used with `oso.build_query` APIs
    """
    if type in ["Actor", "Resource"]:
        raise OsoException(
            f"`type` must be a concrete type, not abstract type `{type}`"
        )
    return QueryVariable(type)


@dataclasses.dataclass(repr=False)
class QueryBuilder:
    """Helper class to support building a custom Oso query.

    Initialize this with `oso.build_query` and chain calls to `and_` and `in_` to add additional constraints.

    After building your query, run it and get the results by calling `evaluate`.
    """

    oso: "Oso"
    predicate: ApiQueryCall
    calls: List[ApiQueryCall] = dataclasses.field(default_factory=list)
    constraints: Dict[QueryId, QueryConstraint] = dataclasses.field(
        default_factory=dict
    )
    context_facts: List[api.ConcreteFact] = dataclasses.field(default_factory=list)

    @classmethod
    def init(cls, oso, fact: QueryArgs) -> Self:
        predicate, *vargs = fact
        this = cls(
            oso=oso,
            # We replace this with a correct value right after this.
            predicate=None,  # type: ignore
        )
        args: List[QueryId] = [this._push_arg(arg) for arg in vargs]
        this.predicate = ApiQueryCall(predicate, args)
        return this

    def and_(self, fact: QueryArgs) -> Self:
        """Add another condition that must be true of the query results.

        For example:
        ```python
        # Query for all the repos on which the given actor can perform the given action,
        # and require the repos to belong to the given folder
        repo = typed_var("Repo")
        authorized_repos_in_folder = (
            oso
              .build_query(("allow", actor, action, repo))
              .and_(("has_relation", repo, "folder", folder))
              .evaluate(repo)
        )
        ```
        """
        predicate, *vargs = fact
        clone = self.clone()
        args: List[QueryId] = [clone._push_arg(arg) for arg in vargs]
        clone.calls.append(ApiQueryCall(predicate, args))
        return clone

    def in_(self, var: QueryVariable, values: List[str]) -> Self:
        """Constrain a query variable to be one of a set of values.

        For example:
        ```python
        repos = ["acme", "anvil"]
        repo = typed_var("Repo")
        action = typed_var("String")
        # Get all the actions the actor can perform on the repos that are in the given set
        authorized_actions = (
            oso
              .build_query(("allow", actor, action, repo))
              .in_(repo, repos)
              .evaluate(action)
        )
        ```
        """
        clone = self.clone()
        name = var.id
        bind = clone.constraints.get(name)
        if bind is None:
            raise OsoException(
                "can only constrain variables that are used in the query"
            )
        if bind.ids is not None:
            raise OsoException("can only set values on each variable once")
        bind.ids = values
        return clone

    def with_context_facts(self, context_facts: Sequence[types.IntoFact]) -> Self:
        """Add context facts to the query."""
        clone = self.clone()
        clone.context_facts.extend(to_api_facts(context_facts))
        return clone

    def _push_arg(self, arg: Value) -> QueryId:
        if isinstance(arg, QueryVariable):
            arg_id = arg.id
            if arg_id not in self.constraints:
                self.constraints[arg_id] = QueryConstraint(type=arg.type, ids=None)
            return arg_id
        else:
            value = to_api_value(arg)
            new_var = QueryVariable(value.type)
            new_id = new_var.id
            self.constraints[new_id] = QueryConstraint(type=value.type, ids=[value.id])
            return new_id

    # Overloads for `evaluate`.
    # Ideally python typing would have a way to express a fn which accepts a Tuple[T, ...] of len L
    # and returns a Tuple[U, ...] of len L.. but it currently does not.
    # We define a handful of common input types and their corresponding output types.
    @overload
    def evaluate(self, arg: None = None) -> bool: ...

    @overload
    def evaluate(self, arg: QueryVariable) -> List[str]: ...

    @overload
    def evaluate(self, arg: Tuple[QueryVariable]) -> List[Tuple[str]]: ...

    @overload
    def evaluate(
        self, arg: Tuple[QueryVariable, QueryVariable]
    ) -> List[Tuple[str, str]]: ...

    @overload
    def evaluate(
        self, arg: Tuple[QueryVariable, QueryVariable, QueryVariable]
    ) -> List[Tuple[str, str, str]]: ...

    @overload
    def evaluate(
        self, arg: Tuple[QueryVariable, QueryVariable, QueryVariable, QueryVariable]
    ) -> List[Tuple[str, str, str, str]]: ...

    @overload
    def evaluate(
        self, arg: Dict[QueryVariable, QueryVariable]
    ) -> Dict[str, List[str]]: ...

    @overload
    def evaluate(
        self, arg: Dict[QueryVariable, Tuple[QueryVariable]]
    ) -> Dict[str, List[Tuple[str]]]: ...

    @overload
    def evaluate(
        self, arg: Dict[QueryVariable, Tuple[QueryVariable, QueryVariable]]
    ) -> Dict[str, List[Tuple[str, str]]]: ...

    @overload
    def evaluate(
        self,
        arg: Dict[QueryVariable, Tuple[QueryVariable, QueryVariable, QueryVariable]],
    ) -> Dict[str, List[Tuple[str, str, str]]]: ...

    @overload
    def evaluate(
        self,
        arg: Dict[
            QueryVariable,
            Tuple[QueryVariable, QueryVariable, QueryVariable, QueryVariable],
        ],
    ) -> Dict[str, List[Tuple[str, str, str, str]]]: ...

    @overload
    def evaluate(
        self, arg: Dict[QueryVariable, Dict[QueryVariable, QueryVariable]]
    ) -> Dict[str, Dict[str, List[str]]]: ...

    # Catchall type hint. Input type too complicated to provide a helpful type hint.
    @overload
    def evaluate(self, arg: EvaluateArg) -> Any: ...

    def evaluate(self, arg=None):  # type: ignore[inconsistent-overload]
        """Evaluate the query. The shape of the return value is determined by what you pass in.

        - If you pass no arguments, returns a boolean. For example:
          ```python
             # true if the given actor can perform the given action on the given resource
             allowed = oso.build_query(("allow", actor, action, resource)).evaluate()
          ```
        - If you pass a variable, returns a list of values for that variable. For example:
          ```python
             action = typed_var("String")
             # all the actions the actor can perform on the given resource- eg. ["read", "write"]
             actions = oso.build_query(("allow", actor, action, resource)).evaluate(action)
          ```
        - If you pass a tuple of variables, returns a list of tuples of values for those variables.
        For example:
          ```python
             action = typed_var("String")
             repo = typed_var("Repo")
             # an array of pairs of allowed actions and repo IDs
             # eg. [["read", "acme"], ["read", "anvil"], ["write", "anvil"]]
             pairs = oso.build_query(("allow", actor, action, repo)).evaluate([action, repo])
          ```
        - If you pass a dict mapping one input variable (call it K) to another
          (call it V), returns a dict of unique values of K to the unique values of
          V for each value of K. For example:
          ```python
             action = typed_var("String")
             repo = typed_var("Repo")
             map = oso.build_query(("allow", actor, action, repo)).evaluate({repo: action})
             # a map of repo IDs to allowed actions-  eg. `{"acme": ["read"], "anvil": ["read", "write"]}`
          ```
        """
        query = self._as_query()
        results = self.oso.api.post_query(query)
        return _evaluate_results(arg, results.results)

    def _as_query(self):
        return dict(
            predicate=dataclasses.astuple(self.predicate),
            calls=list(map(dataclasses.astuple, self.calls)),
            constraints={k: dataclasses.asdict(v) for k, v in self.constraints.items()},
            context_facts=list(map(dataclasses.asdict, self.context_facts)),
        )

    def clone(self):
        return dataclasses.replace(
            self,
            calls=list(self.calls),
            constraints={key: value.clone() for key, value in self.constraints.items()},
            context_facts=list(self.context_facts),
        )

    @overload
    def evaluate_local_select(self) -> str: ...

    @overload
    def evaluate_local_select(
        self, column_names_to_query_vars: Dict[str, QueryVariable]
    ) -> str: ...

    def evaluate_local_select(
        self, column_names_to_query_vars: Optional[Dict[str, QueryVariable]] = None
    ) -> str:
        """Fetches a complete SQL query that can be run against your database, selecting
        a row for each authorized combination of the query variables in `column_names_to_query_vars`
        (ie. combinations of variables that satisfy the Oso query).

        See https://www.osohq.com/docs/app-integration/client-apis/python for examples and
        limitations.

        If you pass an empty dict or omit the parameter entirely, the returned SQL query
        will select a single row with a boolean column called `result`.
        """
        query = self._as_query()
        # The backend wants query var IDs -> column names- invert the map
        query_vars_to_column_names = (
            {}
            if column_names_to_query_vars is None
            else {
                str(query_var.id): column_name
                for column_name, query_var in column_names_to_query_vars.items()
            }
        )
        if column_names_to_query_vars is not None and len(
            query_vars_to_column_names.keys()
        ) != len(column_names_to_query_vars.keys()):
            query_var_histogram = collections.Counter(
                column_names_to_query_vars.values()
            )
            first_dupe = next(
                query_var
                for query_var, count in query_var_histogram.items()
                if count > 1
            )
            raise ValueError(
                f"Found a duplicated {first_dupe.type} variable- you may not select a query variable more than once."
            )
        mode = api.LocalQuerySelect(query_vars_to_column_names)
        result = self.oso.api.post_query_local(query, mode)
        return result.sql

    def evaluate_local_filter(self, column_name: str, query_var: QueryVariable) -> str:
        """Fetches a SQL fragment, which you can embed into the `WHERE` clause of a
        SQL query against your database to filter out unauthorized rows (ie. rows
        that don't satisfy the Oso query).

        See https://www.osohq.com/docs/app-integration/client-apis/python for examples and
        limitations.
        """

        query = self._as_query()
        mode = api.LocalQueryFilter(
            output_column_name=column_name, query_var=query_var.id
        )
        result = self.oso.api.post_query_local(query, mode)
        return result.sql


def _evaluate_results(arg, results):
    if arg is None:
        return bool(results)
    if isinstance(arg, (QueryVariable, list, tuple)):
        evaluated_items = [_evaluate_result_item(arg, r) for r in results]

        # Cannot simply list(set()) due to order
        unique_items = collections.OrderedDict.fromkeys(evaluated_items)
        return list(unique_items.keys())
    structured_grouping = {}
    if len(arg) > 1:
        raise ValueError("`evaluate` cannot accept dicts with >1 elements")
    for v, subarg in arg.items():
        grouping = collections.defaultdict(list)
        for result in results:
            key = _handle_wildcard(result[v.id])
            grouping[key].append(result)
        for key, value in grouping.items():
            structured_grouping[key] = _evaluate_results(subarg, value)
    return structured_grouping


def _evaluate_result_item(arg, result):
    if isinstance(arg, QueryVariable):
        return _handle_wildcard(result[arg.id])
    return tuple(_evaluate_result_item(subarg, result) for subarg in arg)


def _handle_wildcard(v: Optional[str]) -> str:
    return "*" if v is None else v
