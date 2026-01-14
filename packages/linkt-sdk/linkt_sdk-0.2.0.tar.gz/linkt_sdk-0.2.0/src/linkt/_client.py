# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Dict, Mapping, cast
from typing_extensions import Self, Literal, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    not_given,
)
from ._utils import is_given, get_async_library
from ._compat import cached_property
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import LinktError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import icp, run, task, files, sheet, signal
    from .resources.icp import IcpResource, AsyncIcpResource
    from .resources.run import RunResource, AsyncRunResource
    from .resources.task import TaskResource, AsyncTaskResource
    from .resources.files import FilesResource, AsyncFilesResource
    from .resources.signal import SignalResource, AsyncSignalResource
    from .resources.sheet.sheet import SheetResource, AsyncSheetResource

__all__ = [
    "ENVIRONMENTS",
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Linkt",
    "AsyncLinkt",
    "Client",
    "AsyncClient",
]

ENVIRONMENTS: Dict[str, str] = {
    "production": "https://api.linkt.ai",
    "staging": "https://api-staging.linkt.ai",
}


class Linkt(SyncAPIClient):
    # client options
    api_key: str

    _environment: Literal["production", "staging"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["production", "staging"] | NotGiven = not_given,
        base_url: str | httpx.URL | None | NotGiven = not_given,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Linkt client instance.

        This automatically infers the `api_key` argument from the `LINKT_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("LINKT_API_KEY")
        if api_key is None:
            raise LinktError(
                "The api_key client option must be set either by passing api_key to the client or by setting the LINKT_API_KEY environment variable"
            )
        self.api_key = api_key

        self._environment = environment

        base_url_env = os.environ.get("LINKT_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `LINKT_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

    @cached_property
    def icp(self) -> IcpResource:
        from .resources.icp import IcpResource

        return IcpResource(self)

    @cached_property
    def sheet(self) -> SheetResource:
        from .resources.sheet import SheetResource

        return SheetResource(self)

    @cached_property
    def task(self) -> TaskResource:
        from .resources.task import TaskResource

        return TaskResource(self)

    @cached_property
    def signal(self) -> SignalResource:
        from .resources.signal import SignalResource

        return SignalResource(self)

    @cached_property
    def run(self) -> RunResource:
        from .resources.run import RunResource

        return RunResource(self)

    @cached_property
    def files(self) -> FilesResource:
        from .resources.files import FilesResource

        return FilesResource(self)

    @cached_property
    def with_raw_response(self) -> LinktWithRawResponse:
        return LinktWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LinktWithStreamedResponse:
        return LinktWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"x-api-key": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["production", "staging"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncLinkt(AsyncAPIClient):
    # client options
    api_key: str

    _environment: Literal["production", "staging"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["production", "staging"] | NotGiven = not_given,
        base_url: str | httpx.URL | None | NotGiven = not_given,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncLinkt client instance.

        This automatically infers the `api_key` argument from the `LINKT_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("LINKT_API_KEY")
        if api_key is None:
            raise LinktError(
                "The api_key client option must be set either by passing api_key to the client or by setting the LINKT_API_KEY environment variable"
            )
        self.api_key = api_key

        self._environment = environment

        base_url_env = os.environ.get("LINKT_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `LINKT_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

    @cached_property
    def icp(self) -> AsyncIcpResource:
        from .resources.icp import AsyncIcpResource

        return AsyncIcpResource(self)

    @cached_property
    def sheet(self) -> AsyncSheetResource:
        from .resources.sheet import AsyncSheetResource

        return AsyncSheetResource(self)

    @cached_property
    def task(self) -> AsyncTaskResource:
        from .resources.task import AsyncTaskResource

        return AsyncTaskResource(self)

    @cached_property
    def signal(self) -> AsyncSignalResource:
        from .resources.signal import AsyncSignalResource

        return AsyncSignalResource(self)

    @cached_property
    def run(self) -> AsyncRunResource:
        from .resources.run import AsyncRunResource

        return AsyncRunResource(self)

    @cached_property
    def files(self) -> AsyncFilesResource:
        from .resources.files import AsyncFilesResource

        return AsyncFilesResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncLinktWithRawResponse:
        return AsyncLinktWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLinktWithStreamedResponse:
        return AsyncLinktWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"x-api-key": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["production", "staging"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class LinktWithRawResponse:
    _client: Linkt

    def __init__(self, client: Linkt) -> None:
        self._client = client

    @cached_property
    def icp(self) -> icp.IcpResourceWithRawResponse:
        from .resources.icp import IcpResourceWithRawResponse

        return IcpResourceWithRawResponse(self._client.icp)

    @cached_property
    def sheet(self) -> sheet.SheetResourceWithRawResponse:
        from .resources.sheet import SheetResourceWithRawResponse

        return SheetResourceWithRawResponse(self._client.sheet)

    @cached_property
    def task(self) -> task.TaskResourceWithRawResponse:
        from .resources.task import TaskResourceWithRawResponse

        return TaskResourceWithRawResponse(self._client.task)

    @cached_property
    def signal(self) -> signal.SignalResourceWithRawResponse:
        from .resources.signal import SignalResourceWithRawResponse

        return SignalResourceWithRawResponse(self._client.signal)

    @cached_property
    def run(self) -> run.RunResourceWithRawResponse:
        from .resources.run import RunResourceWithRawResponse

        return RunResourceWithRawResponse(self._client.run)

    @cached_property
    def files(self) -> files.FilesResourceWithRawResponse:
        from .resources.files import FilesResourceWithRawResponse

        return FilesResourceWithRawResponse(self._client.files)


class AsyncLinktWithRawResponse:
    _client: AsyncLinkt

    def __init__(self, client: AsyncLinkt) -> None:
        self._client = client

    @cached_property
    def icp(self) -> icp.AsyncIcpResourceWithRawResponse:
        from .resources.icp import AsyncIcpResourceWithRawResponse

        return AsyncIcpResourceWithRawResponse(self._client.icp)

    @cached_property
    def sheet(self) -> sheet.AsyncSheetResourceWithRawResponse:
        from .resources.sheet import AsyncSheetResourceWithRawResponse

        return AsyncSheetResourceWithRawResponse(self._client.sheet)

    @cached_property
    def task(self) -> task.AsyncTaskResourceWithRawResponse:
        from .resources.task import AsyncTaskResourceWithRawResponse

        return AsyncTaskResourceWithRawResponse(self._client.task)

    @cached_property
    def signal(self) -> signal.AsyncSignalResourceWithRawResponse:
        from .resources.signal import AsyncSignalResourceWithRawResponse

        return AsyncSignalResourceWithRawResponse(self._client.signal)

    @cached_property
    def run(self) -> run.AsyncRunResourceWithRawResponse:
        from .resources.run import AsyncRunResourceWithRawResponse

        return AsyncRunResourceWithRawResponse(self._client.run)

    @cached_property
    def files(self) -> files.AsyncFilesResourceWithRawResponse:
        from .resources.files import AsyncFilesResourceWithRawResponse

        return AsyncFilesResourceWithRawResponse(self._client.files)


class LinktWithStreamedResponse:
    _client: Linkt

    def __init__(self, client: Linkt) -> None:
        self._client = client

    @cached_property
    def icp(self) -> icp.IcpResourceWithStreamingResponse:
        from .resources.icp import IcpResourceWithStreamingResponse

        return IcpResourceWithStreamingResponse(self._client.icp)

    @cached_property
    def sheet(self) -> sheet.SheetResourceWithStreamingResponse:
        from .resources.sheet import SheetResourceWithStreamingResponse

        return SheetResourceWithStreamingResponse(self._client.sheet)

    @cached_property
    def task(self) -> task.TaskResourceWithStreamingResponse:
        from .resources.task import TaskResourceWithStreamingResponse

        return TaskResourceWithStreamingResponse(self._client.task)

    @cached_property
    def signal(self) -> signal.SignalResourceWithStreamingResponse:
        from .resources.signal import SignalResourceWithStreamingResponse

        return SignalResourceWithStreamingResponse(self._client.signal)

    @cached_property
    def run(self) -> run.RunResourceWithStreamingResponse:
        from .resources.run import RunResourceWithStreamingResponse

        return RunResourceWithStreamingResponse(self._client.run)

    @cached_property
    def files(self) -> files.FilesResourceWithStreamingResponse:
        from .resources.files import FilesResourceWithStreamingResponse

        return FilesResourceWithStreamingResponse(self._client.files)


class AsyncLinktWithStreamedResponse:
    _client: AsyncLinkt

    def __init__(self, client: AsyncLinkt) -> None:
        self._client = client

    @cached_property
    def icp(self) -> icp.AsyncIcpResourceWithStreamingResponse:
        from .resources.icp import AsyncIcpResourceWithStreamingResponse

        return AsyncIcpResourceWithStreamingResponse(self._client.icp)

    @cached_property
    def sheet(self) -> sheet.AsyncSheetResourceWithStreamingResponse:
        from .resources.sheet import AsyncSheetResourceWithStreamingResponse

        return AsyncSheetResourceWithStreamingResponse(self._client.sheet)

    @cached_property
    def task(self) -> task.AsyncTaskResourceWithStreamingResponse:
        from .resources.task import AsyncTaskResourceWithStreamingResponse

        return AsyncTaskResourceWithStreamingResponse(self._client.task)

    @cached_property
    def signal(self) -> signal.AsyncSignalResourceWithStreamingResponse:
        from .resources.signal import AsyncSignalResourceWithStreamingResponse

        return AsyncSignalResourceWithStreamingResponse(self._client.signal)

    @cached_property
    def run(self) -> run.AsyncRunResourceWithStreamingResponse:
        from .resources.run import AsyncRunResourceWithStreamingResponse

        return AsyncRunResourceWithStreamingResponse(self._client.run)

    @cached_property
    def files(self) -> files.AsyncFilesResourceWithStreamingResponse:
        from .resources.files import AsyncFilesResourceWithStreamingResponse

        return AsyncFilesResourceWithStreamingResponse(self._client.files)


Client = Linkt

AsyncClient = AsyncLinkt
