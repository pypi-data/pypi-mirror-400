import json
import logging
import pathlib
import platform
import typing
import uuid
from dataclasses import asdict, dataclass
from http import HTTPStatus
from json import dumps
from typing import Dict, List, Mapping, Optional, Union

import backoff
import requests
from typing_extensions import TypeAlias

from .version import __version__
from .types import ExpectedResult

logger = logging.getLogger(__name__)

HTTP_ERROR_MAX_RETRIES = 2
HTTP_ERROR_MAX_TIME = 30

NETWORK_ERROR_MAX_RETRIES = 2
NETWORK_ERROR_MAX_TIME = 30

TIMEOUT_INTERVALS = (1, 5)


class OsoException(Exception):
    """Base class for Oso exceptions - throw this for Oso-specific errors instead of Exception."""

    pass


@dataclass
class ApiResult:
    message: str


@dataclass
class Policy:
    filename: Optional[str]
    src: str


@dataclass
class GetPolicyResult:
    policy: Optional[Policy]


@dataclass
class VariableValue:
    type: Optional[str]
    id: Optional[str]


@dataclass
class ConcreteValue:
    type: str
    id: str


@dataclass
class ConcreteFact:
    predicate: str
    args: List[ConcreteValue]

    @classmethod
    def from_json(cls, json):
        return cls(
            predicate=json["predicate"], args=[ConcreteValue(**v) for v in json["args"]]
        )


@dataclass
class VariableFact:
    predicate: str
    args: List[VariableValue]

    @classmethod
    def from_json(cls, json):
        return cls(
            predicate=json["predicate"], args=[VariableValue(**v) for v in json["args"]]
        )


@dataclass
class BatchInserts:
    inserts: List[ConcreteFact]


@dataclass
class BatchDeletes:
    deletes: List[VariableFact]


FactChangeset: TypeAlias = Union[BatchInserts, BatchDeletes]


@dataclass
class AuthorizeResult:
    allowed: bool


@dataclass
class AuthorizeQuery:
    actor_type: str
    actor_id: str
    action: str
    resource_type: str
    resource_id: str
    context_facts: List[ConcreteFact]


@dataclass
class ListResult:
    results: List[str]


@dataclass
class ListQuery:
    actor_type: str
    actor_id: str
    action: str
    resource_type: str
    context_facts: List[ConcreteFact]


@dataclass
class ActionsResult:
    results: List[str]


@dataclass
class ActionsQuery:
    actor_type: str
    actor_id: str
    resource_type: str
    resource_id: str
    context_facts: List[ConcreteFact]


@dataclass
class QueryResult:
    results: List[Dict[str, Optional[str]]]


@dataclass
class StatsResult:
    num_roles: int
    num_relations: int
    num_facts: int


@dataclass
class ResourceMetadata:
    roles: List[str]
    permissions: List[str]
    relations: Mapping[str, str]


@dataclass
class PolicyMetadata:
    resources: Mapping[str, ResourceMetadata]


@dataclass
class LocalQueryResult:
    sql: str


@dataclass
class LocalQuerySelect:
    query_vars_to_output_column_names: Dict[str, str]
    mode: str = "select"  # don't override plz


@dataclass
class LocalQueryFilter:
    output_column_name: str
    query_var: str
    mode: str = "filter"  # don't override plz


LocalQueryMode = Union[LocalQuerySelect, LocalQueryFilter]


# Fatal errors are errors that we do not expect to be able to retry. e.g., a
# 404 error should never succeed even if retries. We define fatal errors as:
# all 400 errors excluding 429.
def _fatal_retry_code(exc: Exception) -> bool:
    if isinstance(exc, requests.exceptions.HTTPError):
        if exc.response.status_code == 429:
            return False
        # Is server error
        elif 500 <= exc.response.status_code <= 599:
            return False
        else:
            return True
    else:
        return False


def _fallback_retryable_status_code(status_code: int) -> bool:
    return (
        # HTTP400 and HTTP5xx indicates errors experienced by the server in
        # handling the request, so these should be retried against fallback
        status_code == HTTPStatus.BAD_REQUEST
        or 500 <= status_code <= 599
    )


def _handle_error(exc: requests.exceptions.HTTPError):
    code, text = exc.response.status_code, exc.response.text
    msg = f"Oso Server error: {code}\n{text}"
    raise OsoException(msg)


def _raise_for_bad_statuses(response):
    if isinstance(response.status_code, int) and (
        response.status_code < 200 or response.status_code >= 300
    ):
        raise requests.exceptions.HTTPError(
            f"{response.status_code} Client Error: {response.url} for url: {response.url}",
            response=response,
        )


class API:
    def __init__(
        self,
        url="https://api.osohq.com",
        api_key=None,
        fallback_url=None,
        *,
        data_bindings=None,
    ):
        self.url = url
        if not self.url.endswith("/"):
            self.url += "/"
        self.api_base = "api"
        self.user_agent = (
            f"Oso Cloud (python {platform.python_version()}; rv:{__version__})"
        )
        self.client_id = str(uuid.uuid4())
        if api_key:
            self.token = api_key
        else:
            raise ValueError("Must set an api_key")
        self.session = requests.Session()
        self.session.headers.update(self._default_headers())

        self.fallback_url = fallback_url
        if self.fallback_url:
            if not self.fallback_url.endswith("/"):
                self.fallback_url += "/"
            self.fallback_session = requests.Session()
            self.fallback_session.headers.update(self._default_headers())

        self.data_bindings = None
        if data_bindings:
            self.data_bindings = pathlib.Path(data_bindings).read_text()

    def _handle_result(self, result, is_mutation=False):
        try:
            if is_mutation:
                self._set_last_offset(result)
            return result.json()
        except json.decoder.JSONDecodeError:
            raise OsoException("Oso failed to deserialize results: ", result.text)

    def _fallback_eligible(self, method: str, path: str):
        if not self.fallback_url:
            return False

        if method == "post" and path in [
            "/authorize",
            "/authorize_resources",
            "/list",
            "/actions",
            "/query",
            # Distributed check APIs
            "/actions_query",
            "/authorize_query",
            "/list_query",
            "/evaluate_query_local",
            # Query Builder APIs
            "/evaluate_query",
        ]:
            return True
        elif method == "get" and path in [
            "/facts",
            "/policy_metadata",
        ]:
            return True
        else:
            return False

    def _default_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": self.user_agent,
            "X-OsoApiVersion": "0",
            "Accept": "application/json",
            "X-Oso-Instance-Id": self.client_id,
        }

    def _set_last_offset(self, result):
        last_offset = result.headers.get("OsoOffset")
        if last_offset:
            self.session.headers.update({"OsoOffset": last_offset})

    def _do_post(self, path, params, json, fallback=False):
        @backoff.on_exception(
            backoff.expo,
            (requests.exceptions.ConnectionError, requests.exceptions.Timeout),
            max_time=NETWORK_ERROR_MAX_TIME,
            max_tries=NETWORK_ERROR_MAX_RETRIES,
        )
        @backoff.on_exception(
            backoff.expo,
            requests.exceptions.HTTPError,
            max_time=HTTP_ERROR_MAX_TIME,
            max_tries=HTTP_ERROR_MAX_RETRIES,
            giveup=_fatal_retry_code,
        )
        def _do_post_inner(session, url, path, params, json):
            headers = {"X-Request-ID": str(uuid.uuid4())}

            json_str = dumps(json)
            body_size_bytes = len(json_str.encode("utf-8"))

            max_body_size = 10 * 1024 * 1024  # 10MB in bytes
            if body_size_bytes > max_body_size:
                raise ValueError(
                    f"Request payload too large (body_size_bytes: {body_size_bytes}, max_body_size {max_body_size})"
                )

            response = session.post(
                f"{url}{self.api_base}{path}",
                params=params,
                json=json,
                headers=headers,
                timeout=TIMEOUT_INTERVALS,
            )

            _raise_for_bad_statuses(response)
            return response

        # We first try the request against Oso Cloud. `backoff` will retry the
        # request on configured errors. If the request still fails after the
        # maximum retry attempts, fallback is configured, and the request is
        # supported by fallback, then the request is tried against fallback.
        # `backoff` is also used to retry requests against fallback on
        # configured errors.
        try_fallback = False
        try:
            return _do_post_inner(self.session, self.url, path, params, json)
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as exc:
            if self._fallback_eligible("post", path):
                try_fallback = True
            else:
                raise exc
        except requests.exceptions.HTTPError as exc:
            if self._fallback_eligible(
                "post", path
            ) and _fallback_retryable_status_code(exc.response.status_code):
                try_fallback = True
            else:
                raise exc
        if try_fallback:
            logger.info(f"_do_post: falling back to {self.fallback_url}")
            return _do_post_inner(
                self.fallback_session, self.fallback_url, path, params, json
            )

    def _do_get(self, path, params, json):
        @backoff.on_exception(
            backoff.expo,
            (requests.exceptions.ConnectionError, requests.exceptions.Timeout),
            max_time=NETWORK_ERROR_MAX_TIME,
            max_tries=NETWORK_ERROR_MAX_RETRIES,
        )
        @backoff.on_exception(
            backoff.expo,
            requests.exceptions.HTTPError,
            max_time=HTTP_ERROR_MAX_TIME,
            max_tries=HTTP_ERROR_MAX_RETRIES,
            giveup=_fatal_retry_code,
        )
        def _do_get_inner(session, url, path, params, json):
            headers = {"X-Request-ID": str(uuid.uuid4())}
            response = session.get(
                f"{url}{self.api_base}{path}",
                params=params,
                json=json,
                headers=headers,
                timeout=TIMEOUT_INTERVALS,
            )
            _raise_for_bad_statuses(response)
            return response

        # We first try the request against Oso Cloud. `backoff` will retry the
        # request on configured errors. If the request still fails after the
        # maximum retry attempts, fallback is configured, and the request is
        # supported by fallback, then the request is tried against fallback.
        # `backoff` is also used to retry requests against fallback on
        # configured errors.
        try_fallback = False
        try:
            return _do_get_inner(self.session, self.url, path, params, json)
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as exc:
            if self._fallback_eligible("get", path):
                try_fallback = True
            else:
                raise exc
        except (requests.exceptions.HTTPError,) as exc:
            if self._fallback_eligible("get", path) and _fallback_retryable_status_code(
                exc.response.status_code
            ):
                try_fallback = True
            else:
                raise exc
        if try_fallback:
            logger.info(f"_do_get: falling back to {self.fallback_url}")
            return _do_get_inner(
                self.fallback_session, self.fallback_url, path, params, json
            )

    def _do_delete(self, path, params, json):
        @backoff.on_exception(
            backoff.expo,
            (requests.exceptions.ConnectionError, requests.exceptions.Timeout),
            max_time=NETWORK_ERROR_MAX_TIME,
            max_tries=NETWORK_ERROR_MAX_RETRIES,
        )
        @backoff.on_exception(
            backoff.expo,
            requests.exceptions.HTTPError,
            max_time=HTTP_ERROR_MAX_TIME,
            max_tries=HTTP_ERROR_MAX_RETRIES,
            giveup=_fatal_retry_code,
        )
        def _do_delete_inner(session, url, path, params, json):
            headers = {"X-Request-ID": str(uuid.uuid4())}

            json_str = dumps(json)
            body_size_bytes = len(json_str.encode("utf-8"))

            max_body_size = 10 * 1024 * 1024  # 10MB in bytes
            if body_size_bytes > max_body_size:
                raise ValueError(
                    f"Request payload too large (body_size_bytes: {body_size_bytes}, max_body_size {max_body_size})"
                )

            response = session.delete(
                f"{url}{self.api_base}{path}",
                params=params,
                json=json,
                headers=headers,
                timeout=TIMEOUT_INTERVALS,
            )
            _raise_for_bad_statuses(response)
            return response

        # We first try the request against Oso Cloud. `backoff` will retry the
        # request on configured errors. If the request still fails after the
        # maximum retry attempts, fallback is configured, and the request is
        # supported by fallback, then the request is tried against fallback.
        # `backoff` is also used to retry requests against fallback on
        # configured errors.
        try_fallback = False
        try:
            return _do_delete_inner(self.session, self.url, path, params, json)
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as exc:
            if self._fallback_eligible("delete", path):
                try_fallback = True
            else:
                raise exc
        except (requests.exceptions.HTTPError,) as exc:
            if self._fallback_eligible(
                "delete", path
            ) and _fallback_retryable_status_code(exc.response.status_code):
                try_fallback = True
            else:
                raise exc
        if try_fallback:
            logger.info(f"_do_delete: falling back to {self.fallback_url}")
            return _do_delete_inner(
                self.fallback_session, self.fallback_url, path, params, json
            )

    def get_policy(self):
        params = None
        json = None
        try:
            result = self._do_get("/policy", params=params, json=json)
            response = self._handle_result(result)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return GetPolicyResult(**response)

    def post_policy(self, data):
        params = None
        json = asdict(data)
        try:
            result = self._do_post("/policy", params=params, json=json)
            response = self._handle_result(result, True)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return ApiResult(**response)

    def post_batch(self, data: List[FactChangeset]):
        params = None
        _json = list(map(asdict, data))
        try:
            result = self._do_post("/batch", params=params, json=_json)
            response = self._handle_result(result, True)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return ApiResult(**response)

    def post_authorize(self, data, parity_handle=None):
        params = None
        json = asdict(data)
        try:
            result = self._do_post("/authorize", params=params, json=json)
            if parity_handle is not None:
                request_id = result.headers.get("X-Request-ID")
                if request_id is None:
                    raise OsoException(
                        "Unable to use Parity Handle: no request ID returned from Oso."
                    )
                parity_handle._set(request_id, self)
            response = self._handle_result(result)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return AuthorizeResult(**response)

    def post_list(self, data):
        params = None
        json = asdict(data)
        try:
            result = self._do_post("/list", params=params, json=json)
            response = self._handle_result(result)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return ListResult(**response)

    def post_actions(self, data):
        params = None
        json = asdict(data)
        try:
            result = self._do_post("/actions", params=params, json=json)
            response = self._handle_result(result)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return ActionsResult(**response)

    def get_stats(self):
        params = None
        json = None
        try:
            result = self._do_get("/stats", params=params, json=json)
            response = self._handle_result(result)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return StatsResult(**response)

    def post_authorize_query(self, query, parity_handle=None):
        params = None
        json = {
            "query": asdict(query),
            "data_bindings": self.data_bindings,
        }
        try:
            result = self._do_post("/authorize_query", params=params, json=json)
            if parity_handle is not None:
                request_id = result.headers.get("X-Request-ID")
                if request_id is None:
                    raise OsoException(
                        "Unable to use Parity Handle: no request ID returned from Oso."
                    )
                parity_handle._set(request_id, self)
            response = self._handle_result(result)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return LocalQueryResult(**response)

    def post_list_query(self, query, column):
        params = None
        json = {
            "query": asdict(query),
            "column": column,
            "data_bindings": self.data_bindings,
        }
        try:
            result = self._do_post("/list_query", params=params, json=json)
            response = self._handle_result(result)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return LocalQueryResult(**response)

    def post_actions_query(self, query):
        params = None
        json = {
            "query": asdict(query),
            "data_bindings": self.data_bindings,
        }
        try:
            result = self._do_post("/actions_query", params=params, json=json)
            response = self._handle_result(result)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return LocalQueryResult(**response)

    def post_query_local(self, query, mode: LocalQueryMode):
        params = None
        json = {
            "query": query,
            "data_bindings": self.data_bindings,
            "mode": asdict(mode),
        }
        try:
            result = self._do_post("/evaluate_query_local", params=params, json=json)
            response = self._handle_result(result)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return LocalQueryResult(**response)

    def clear_data(self):
        params = None
        json = None
        try:
            result = self._do_post("/clear_data", params=params, json=json)
            response = self._handle_result(result, True)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return ApiResult(**response)

    def get_facts(self, predicate: str, args: List[VariableValue]):
        params = {}
        params["predicate"] = predicate
        for i, arg in enumerate(args):
            if arg.type is not None:
                params[f"args.{i}.type"] = arg.type
            if arg.id is not None:
                params[f"args.{i}.id"] = arg.id
        json = None
        try:
            result = self._do_get("/facts", params=params, json=json)
            response = self._handle_result(result)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        result = []
        for item in response:
            result.append(ConcreteFact.from_json(item))
        return result

    def post_query(self, data):
        params = None
        try:
            result = self._do_post("/evaluate_query", params=params, json=data)
            response = self._handle_result(result)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return QueryResult(response["results"])

    def get_policy_metadata(self, version: Optional[int] = None) -> PolicyMetadata:
        params = {"version": version}
        try:
            result = self._do_get("/policy_metadata", params=params, json=None)
            response: typing.Any = self._handle_result(result)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        metadata = response["metadata"]
        return PolicyMetadata(
            resources={
                k: ResourceMetadata(**v) for k, v in metadata["resources"].items()
            }
        )

    def post_expected_result(self, expected_result):
        params = None
        if not isinstance(expected_result, ExpectedResult):
            raise TypeError("Invalid ExpectedResult object.")
        json = asdict(expected_result)
        try:
            result = self._do_post("/expect", params=params, json=json)
            response = self._handle_result(result, True)
        except requests.exceptions.HTTPError as exc:
            _handle_error(exc)
        return ApiResult(**response)
