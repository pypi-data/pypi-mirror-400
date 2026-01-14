from typing import Generator, List, Optional
from contextlib import contextmanager
from uuid import UUID

from . import api
from .parity_handle import ParityHandle
from .types import (
    Fact,
    IntoFact,
    IntoFactPattern,
    Value,
)
from .helpers import (
    to_api_fact,
    to_api_value,
    from_api_facts,
    to_api_facts,
    to_api_variable_fact,
)
from .query import (
    QueryArgs,
    QueryBuilder,
)
from .for_agents import ForAgents


class Oso:
    """Oso Cloud client

    For more detailed documentation, see
    https://www.osohq.com/docs/app-integration/client-apis/python
    """

    def __init__(
        self,
        url: str = "https://api.osohq.com",
        api_key=None,
        fallback_url=None,
        *,
        data_bindings=None,
    ):
        self.api = api.API(url, api_key, fallback_url, data_bindings=data_bindings)

    def authorize(
        self,
        actor: Value,
        action: str,
        resource: Value,
        context_facts: Optional[List[IntoFact]] = None,
        parity_handle: Optional[ParityHandle] = None,
    ) -> bool:
        """Check a permission:

        :return: true if the actor can perform the action on the resource;
        otherwise false.
        """
        if parity_handle is not None and not isinstance(parity_handle, ParityHandle):
            raise TypeError("parity_handle must be an instance of ParityHandle")

        if isinstance(context_facts, ParityHandle):
            raise ValueError(
                "Received a ParityHandle as the 'context_facts' argument."
                "parity_handle must be passed as a keyword argument, e.g. parity_handle=parity_handle"
            )

        actor_typed_id = to_api_value(actor)
        resource_typed_id = to_api_value(resource)
        data = api.AuthorizeQuery(
            actor_typed_id.type,
            actor_typed_id.id,
            action,
            resource_typed_id.type,
            resource_typed_id.id,
            to_api_facts(context_facts),
        )
        result = self.api.post_authorize(data, parity_handle)
        return result.allowed

    def list(
        self,
        actor: Value,
        action: str,
        resource_type: str,
        context_facts: Optional[List[IntoFact]] = None,
    ) -> List[str]:
        """List authorized resources:

        Fetches a list of resource ids on which an actor can perform a
        particular action.
        """
        actor_typed_id = to_api_value(actor)
        data = api.ListQuery(
            actor_typed_id.type,
            actor_typed_id.id,
            action,
            resource_type,
            to_api_facts(context_facts),
        )
        result = self.api.post_list(data)
        return result.results

    def actions(
        self,
        actor: Value,
        resource: Value,
        context_facts: Optional[List[IntoFact]] = None,
    ) -> List[str]:
        """List authorized actions:

        Fetches a list of actions which an actor can perform on a particular resource.
        """
        actor_typed_id = to_api_value(actor)
        resource_typed_id = to_api_value(resource)
        data = api.ActionsQuery(
            actor_typed_id.type,
            actor_typed_id.id,
            resource_typed_id.type,
            resource_typed_id.id,
            to_api_facts(context_facts),
        )
        result = self.api.post_actions(data)
        return result.results

    def insert(self, fact: IntoFact):
        """Add a fact:

        Adds a fact with the given name and arguments.
        """
        api_fact = to_api_fact(fact)
        self.api.post_batch([api.BatchInserts(inserts=[api_fact])])

    def delete(self, fact: IntoFactPattern):
        """Delete fact:

        Deletes a fact. Does not throw an error if there were no matching facts to delete.

        You can delete many facts at once by using the `None` wildcard or `ValueOfType("MyType")`
        for any of the fact arguments- eg.
        `oso.delete(("has_role", Value("User", "bob"), None, Value("Repository", "acme")))`
        will delete all the roles that User bob has on Repository acme, and
        `oso.delete(("has_role", ValueOfType("User"), None, ValueOfType("Repository"))`
        will delete all the roles that any User has on any Repository.
        """
        api_fact = to_api_variable_fact(fact)
        self.api.post_batch([api.BatchDeletes(deletes=[api_fact])])

    @contextmanager
    def batch(self) -> Generator["BatchTransaction", None, None]:
        """Batch transaction:

        Insert and delete many facts in a single API call.
        Example:
        with oso.batch() as tx:
          tx.insert(fact1)
          tx.insert(fact2)
          tx.delete(fact3)
        """
        tx = BatchTransaction()
        yield tx
        if tx.changesets:
            self.api.post_batch(tx.changesets)

    def get(self, fact: IntoFactPattern) -> List[Fact]:
        """List facts:

        Lists facts that are stored in Oso Cloud. Can be used to check the existence
        of a particular fact, or used to fetch all facts that have a particular
        argument.

        You can pass wildcards into this function to get facts whose arguments match a certain
        type, or anything at all.

        Example:
        oso.get(("has_role", ValueOfType("User"), "member", None))
        # fetches has_role facts where the first argument is a User, the second
        # argument is the string "member", and the third argument is anything
        """
        variable_fact = to_api_variable_fact(fact)
        result = self.api.get_facts(variable_fact.predicate, variable_fact.args)
        return from_api_facts(result)

    def policy(self, policy: str):
        """Update the active policy:

        Updates the policy in Oso Cloud. The string passed into this method should be
        written in Polar.
        """
        policy_obj: api.Policy = api.Policy("", policy)
        self.api.post_policy(policy_obj)

    def get_policy_metadata(self) -> api.PolicyMetadata:
        """Get metadata about the currently active policy."""
        return self.api.get_policy_metadata()

    # Local Filtering Methods:
    def authorize_local(
        self,
        actor,
        action,
        resource,
        context_facts: Optional[List[IntoFact]] = None,
        parity_handle: Optional[ParityHandle] = None,
    ) -> str:
        """Fetches a query that can be run against your database to determine whether
        an actor can perform an action on a resource."""
        if parity_handle is not None and not isinstance(parity_handle, ParityHandle):
            raise TypeError("parity_handle must be an instance of ParityHandle")

        if isinstance(context_facts, ParityHandle):
            raise ValueError(
                "Received a ParityHandle as the 'context_facts' argument. "
                "parity_handle must be passed as a keyword argument, e.g. parity_handle=parity_handle"
            )

        actor_typed_id = to_api_value(actor)
        resource_typed_id = to_api_value(resource)
        data = api.AuthorizeQuery(
            actor_typed_id.type,
            actor_typed_id.id,
            action,
            resource_typed_id.type,
            resource_typed_id.id,
            to_api_facts(context_facts),
        )
        result = self.api.post_authorize_query(data, parity_handle)
        return result.sql

    def list_local(
        self,
        actor,
        action,
        resource_type,
        column,
        context_facts: Optional[List[IntoFact]] = None,
    ) -> str:
        """Fetches a filter that can be applied to a database query to return just
        the resources on which an actor can perform an action."""
        actor_typed_id = to_api_value(actor)
        data = api.ListQuery(
            actor_typed_id.type,
            actor_typed_id.id,
            action,
            resource_type,
            to_api_facts(context_facts),
        )
        result = self.api.post_list_query(data, column)
        return result.sql

    def actions_local(
        self,
        actor,
        resource,
        context_facts: Optional[List[IntoFact]] = None,
    ) -> str:
        """Fetches a query that can be run against your database to determine the actions
        an actor can perform on a resource."""
        actor_typed_id = to_api_value(actor)
        resource_typed_id = to_api_value(resource)
        data = api.ActionsQuery(
            actor_typed_id.type,
            actor_typed_id.id,
            resource_typed_id.type,
            resource_typed_id.id,
            to_api_facts(context_facts),
        )
        result = self.api.post_actions_query(data)
        return result.sql

    def build_query(self, query: QueryArgs) -> QueryBuilder:
        """Query for an arbitrary expression.

        Use `typed_var` to create variables to use in the query,
        and refer to them in the final `evaluate` call to get their values."""
        return QueryBuilder.init(self, query)

    def for_agents(
        self, agent_id: str, session_id: UUID, users: List[Value], **extra
    ) -> ForAgents:
        """Creates an object for tracking agent events.

        Use this to send agent-related events to Oso for Agents for observability
        and security analysis of AI agent behavior.

        :param agent_id: A unique identifier for the agent.
        :param session_id: A UUID representing the session. Each session groups related
            agent events together.
        :param users: A list of users associated with this agent session. Users are
            represented as Value objects (e.g., Value("User", "user_id")).
        :param extra: Additional metadata to include with all events.
        :return: An object that can be used to send events such as tool calls,
            messages, and errors.

        Example:
            >>> session_id = uuid4()
            >>> for_agents = oso.for_agents(
            ...     "agent-123",
            ...     session_id,
            ...     [Value("User", "alice")]
            ... )
            >>> for_agents.tool_call_request("get_weather", {"location": "SF"})
            >>> for_agents.tool_call_response("get_weather", {"temp": 72})
        """
        return ForAgents(self.api, agent_id, session_id, users, **extra)


class BatchTransaction:
    def __init__(self):
        self.changesets: List[api.FactChangeset] = []

    def insert(self, fact: IntoFact):
        api_fact = to_api_fact(fact)
        last_changeset = self.changesets[-1] if len(self.changesets) > 0 else None
        if isinstance(last_changeset, api.BatchInserts):
            last_changeset.inserts.append(api_fact)
        else:
            self.changesets.append(api.BatchInserts(inserts=[api_fact]))

    def delete(self, fact: IntoFactPattern):
        api_fact = to_api_variable_fact(fact)
        last_changeset = self.changesets[-1] if len(self.changesets) > 0 else None
        if isinstance(last_changeset, api.BatchDeletes):
            last_changeset.deletes.append(api_fact)
        else:
            self.changesets.append(api.BatchDeletes(deletes=[api_fact]))
