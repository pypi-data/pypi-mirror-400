from dataclasses import asdict, dataclass
from typing import List, Dict, Optional
from uuid import uuid4, UUID
from .api import API
from .types import Value
import logging
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


@dataclass
class EventBase:
    agent_id: str
    session_id: str
    users: List[Value]


@dataclass
class ToolCallRequest:
    tool_name: str
    tool_parameters: Dict


@dataclass
class ToolCallResponse:
    tool_name: str
    tool_result: Dict


@dataclass
class ToolCallError:
    tool_name: str


@dataclass
class MessageFromUser:
    message: str


@dataclass
class MessageToUser:
    message: str


class ForAgents:
    """Track agent events for monitoring and security analysis.

    This class provides methods to send agent-related events to Oso for Agents,
    including tool calls, messages, and errors. All events are automatically
    associated with the agent, session, and users specified when this object
    was created.

    Typically created via `Oso.for_agents()` rather than directly instantiated.
    """

    api: API
    base: Dict
    extra: Dict

    def __init__(
        self,
        api: API,
        agent_id: str,
        session_id: Optional[UUID],
        users: Optional[List[Value]],
        **extra,
    ):
        self.api = api
        if session_id is None:
            # TODO: uuidv7
            logger.info("No session ID provided, generating a new one.")
            session_id = uuid4()
        users = users if users is not None else []
        self.base = {**extra, **asdict(EventBase(agent_id, str(session_id), users))}

    def _send(self, path: str, body, extra: Dict):
        json = {
            **self.base,
            **extra,
            **asdict(body),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        try:
            self.api._do_post(path, params=None, json=json)
        except Exception as e:
            logger.error(f"Failed to send event: {e}")

    def tool_call_request(self, tool_name: str, tool_parameters: Dict, **extra):
        """Record when an agent requests to call a tool.

        Send an event indicating that the agent is requesting to execute a tool
        with the specified parameters.

        :param tool_name: The name of the tool being requested.
        :param tool_parameters: A dictionary of parameters to pass to the tool.
        :param extra: Additional metadata to include with the event.
        """
        body = ToolCallRequest(tool_name=tool_name, tool_parameters=tool_parameters)
        self._send("/agents/event/tool_call_request", body, extra)

    def tool_call_response(self, tool_name: str, tool_result: Dict, **extra):
        """Record the result of a successful tool call.

        Send an event with the result returned by a tool after it has been
        successfully executed.

        :param tool_name: The name of the tool that was called.
        :param tool_result: A dictionary containing the result returned by the tool.
        :param extra: Additional metadata to include with the event.
        """
        body = ToolCallResponse(tool_name=tool_name, tool_result=tool_result)
        self._send("/agents/event/tool_call_response", body, extra)

    def tool_call_error(self, tool_name: str, **extra):
        """Record when a tool call fails or encounters an error.

        Send an event indicating that a tool call failed to execute successfully.

        :param tool_name: The name of the tool that encountered an error.
        :param extra: Additional metadata to include with the event, such as error details.
        """
        body = ToolCallError(tool_name=tool_name)
        self._send("/agents/event/tool_call_error", body, extra)

    def message_from_user(self, message: str, **extra):
        """Record a message sent from a user to the agent.

        Send an event capturing user input or messages directed to the agent.

        :param message: The message content from the user.
        :param extra: Additional metadata to include with the event.
        """
        body = MessageFromUser(message=message)
        self._send("/agents/event/message_from_user", body, extra)

    def message_to_user(self, message: str, **extra):
        """Record a message sent from the agent to a user.

        Send an event capturing agent responses or messages directed to the user.

        :param message: The message content from the agent.
        :param extra: Additional metadata to include with the event.
        """
        body = MessageToUser(message=message)
        self._send("/agents/event/message_to_user", body, extra)
