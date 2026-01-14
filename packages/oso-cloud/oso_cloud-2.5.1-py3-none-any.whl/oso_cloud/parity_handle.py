from .types import ExpectedResult


class ParityHandle:
    """
    A testing utility in Oso Migrate for comparing expected authorization
    decisions with actual Oso results.
    """

    def __init__(self):
        self.api = None
        self.request_id = None
        self.expected = None

    def _set(self, request_id, api):
        """
        Internal method called by the API class after authorize.

        Args:
            request_id: The ID of the authorization request.
            api: Reference to the API instance.

         Raises:
            RuntimeError: If request_id is attempted to be set twice.
        """
        if self.request_id is not None:
            raise RuntimeError(
                f"Attempted to set request_id twice. Only one request is allowed per ParityHandle instance."
                f"Original request_id: {self.request_id}"
            )

        self.request_id = request_id
        self.api = api

        if self.expected is not None:
            self._send()

    def expect(self, expected: bool):
        """
        Public method for users to indicate the expected result of an authorization query.

        Args:
            expected: Boolean indicating the expected authorization result.

        Raises:
            TypeError: If expected is not a boolean.
            RuntimeError: If expected result is set twice.
        """

        if not isinstance(expected, bool):
            raise TypeError("Expected a boolean value.")
        if self.expected is not None:
            raise RuntimeError(
                f"Attempted to set expected result twice. Original request_id: {self.request_id}"
            )

        self.expected = expected

        if self.request_id is not None:
            self._send()

    def _send(self):
        if self.api is None or self.request_id is None or self.expected is None:
            raise RuntimeError(
                "API, request_id, and expected must all be set before sending."
            )
        self.api.post_expected_result(ExpectedResult(self.request_id, self.expected))
