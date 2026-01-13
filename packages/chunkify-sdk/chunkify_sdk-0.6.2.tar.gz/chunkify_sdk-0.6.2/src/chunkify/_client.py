# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Headers,
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
from ._exceptions import APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import jobs, files, tokens, sources, uploads, projects, storages, webhooks, notifications
    from .resources.files import FilesResource, AsyncFilesResource
    from .resources.tokens import TokensResource, AsyncTokensResource
    from .resources.sources import SourcesResource, AsyncSourcesResource
    from .resources.uploads import UploadsResource, AsyncUploadsResource
    from .resources.projects import ProjectsResource, AsyncProjectsResource
    from .resources.storages import StoragesResource, AsyncStoragesResource
    from .resources.webhooks import WebhooksResource, AsyncWebhooksResource
    from .resources.jobs.jobs import JobsResource, AsyncJobsResource
    from .resources.notifications import NotificationsResource, AsyncNotificationsResource

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Chunkify",
    "AsyncChunkify",
    "Client",
    "AsyncClient",
]


class Chunkify(SyncAPIClient):
    # client options
    project_access_token: str | None
    team_access_token: str | None
    webhook_key: str | None

    def __init__(
        self,
        *,
        project_access_token: str | None = None,
        team_access_token: str | None = None,
        webhook_key: str | None = None,
        base_url: str | httpx.URL | None = None,
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
        """Construct a new synchronous Chunkify client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `project_access_token` from `CHUNKIFY_TOKEN`
        - `team_access_token` from `CHUNKIFY_TEAM_TOKEN`
        - `webhook_key` from `CHUNKIFY_WEBHOOK_SECRET`
        """
        if project_access_token is None:
            project_access_token = os.environ.get("CHUNKIFY_TOKEN")
        self.project_access_token = project_access_token

        if team_access_token is None:
            team_access_token = os.environ.get("CHUNKIFY_TEAM_TOKEN")
        self.team_access_token = team_access_token

        if webhook_key is None:
            webhook_key = os.environ.get("CHUNKIFY_WEBHOOK_SECRET")
        self.webhook_key = webhook_key

        if base_url is None:
            base_url = os.environ.get("CHUNKIFY_BASE_URL")
        if base_url is None:
            base_url = f"https://api.chunkify.dev/v1"

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
    def files(self) -> FilesResource:
        from .resources.files import FilesResource

        return FilesResource(self)

    @cached_property
    def jobs(self) -> JobsResource:
        from .resources.jobs import JobsResource

        return JobsResource(self)

    @cached_property
    def notifications(self) -> NotificationsResource:
        from .resources.notifications import NotificationsResource

        return NotificationsResource(self)

    @cached_property
    def projects(self) -> ProjectsResource:
        from .resources.projects import ProjectsResource

        return ProjectsResource(self)

    @cached_property
    def sources(self) -> SourcesResource:
        from .resources.sources import SourcesResource

        return SourcesResource(self)

    @cached_property
    def storages(self) -> StoragesResource:
        from .resources.storages import StoragesResource

        return StoragesResource(self)

    @cached_property
    def tokens(self) -> TokensResource:
        from .resources.tokens import TokensResource

        return TokensResource(self)

    @cached_property
    def uploads(self) -> UploadsResource:
        from .resources.uploads import UploadsResource

        return UploadsResource(self)

    @cached_property
    def webhooks(self) -> WebhooksResource:
        from .resources.webhooks import WebhooksResource

        return WebhooksResource(self)

    @cached_property
    def with_raw_response(self) -> ChunkifyWithRawResponse:
        return ChunkifyWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChunkifyWithStreamedResponse:
        return ChunkifyWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="repeat")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        return {**self._project_access_token, **self._team_access_token}

    @property
    def _project_access_token(self) -> dict[str, str]:
        project_access_token = self.project_access_token
        if project_access_token is None:
            return {}
        return {"Authorization": f"Bearer {project_access_token}"}

    @property
    def _team_access_token(self) -> dict[str, str]:
        team_access_token = self.team_access_token
        if team_access_token is None:
            return {}
        return {"Authorization": f"Bearer {team_access_token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    @override
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if self.project_access_token and headers.get("Authorization"):
            return
        if isinstance(custom_headers.get("Authorization"), Omit):
            return

        if self.team_access_token and headers.get("Authorization"):
            return
        if isinstance(custom_headers.get("Authorization"), Omit):
            return

        raise TypeError(
            '"Could not resolve authentication method. Expected either project_access_token or team_access_token to be set. Or for one of the `Authorization` or `Authorization` headers to be explicitly omitted"'
        )

    def copy(
        self,
        *,
        project_access_token: str | None = None,
        team_access_token: str | None = None,
        webhook_key: str | None = None,
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
            project_access_token=project_access_token or self.project_access_token,
            team_access_token=team_access_token or self.team_access_token,
            webhook_key=webhook_key or self.webhook_key,
            base_url=base_url or self.base_url,
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


class AsyncChunkify(AsyncAPIClient):
    # client options
    project_access_token: str | None
    team_access_token: str | None
    webhook_key: str | None

    def __init__(
        self,
        *,
        project_access_token: str | None = None,
        team_access_token: str | None = None,
        webhook_key: str | None = None,
        base_url: str | httpx.URL | None = None,
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
        """Construct a new async AsyncChunkify client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `project_access_token` from `CHUNKIFY_TOKEN`
        - `team_access_token` from `CHUNKIFY_TEAM_TOKEN`
        - `webhook_key` from `CHUNKIFY_WEBHOOK_SECRET`
        """
        if project_access_token is None:
            project_access_token = os.environ.get("CHUNKIFY_TOKEN")
        self.project_access_token = project_access_token

        if team_access_token is None:
            team_access_token = os.environ.get("CHUNKIFY_TEAM_TOKEN")
        self.team_access_token = team_access_token

        if webhook_key is None:
            webhook_key = os.environ.get("CHUNKIFY_WEBHOOK_SECRET")
        self.webhook_key = webhook_key

        if base_url is None:
            base_url = os.environ.get("CHUNKIFY_BASE_URL")
        if base_url is None:
            base_url = f"https://api.chunkify.dev/v1"

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
    def files(self) -> AsyncFilesResource:
        from .resources.files import AsyncFilesResource

        return AsyncFilesResource(self)

    @cached_property
    def jobs(self) -> AsyncJobsResource:
        from .resources.jobs import AsyncJobsResource

        return AsyncJobsResource(self)

    @cached_property
    def notifications(self) -> AsyncNotificationsResource:
        from .resources.notifications import AsyncNotificationsResource

        return AsyncNotificationsResource(self)

    @cached_property
    def projects(self) -> AsyncProjectsResource:
        from .resources.projects import AsyncProjectsResource

        return AsyncProjectsResource(self)

    @cached_property
    def sources(self) -> AsyncSourcesResource:
        from .resources.sources import AsyncSourcesResource

        return AsyncSourcesResource(self)

    @cached_property
    def storages(self) -> AsyncStoragesResource:
        from .resources.storages import AsyncStoragesResource

        return AsyncStoragesResource(self)

    @cached_property
    def tokens(self) -> AsyncTokensResource:
        from .resources.tokens import AsyncTokensResource

        return AsyncTokensResource(self)

    @cached_property
    def uploads(self) -> AsyncUploadsResource:
        from .resources.uploads import AsyncUploadsResource

        return AsyncUploadsResource(self)

    @cached_property
    def webhooks(self) -> AsyncWebhooksResource:
        from .resources.webhooks import AsyncWebhooksResource

        return AsyncWebhooksResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncChunkifyWithRawResponse:
        return AsyncChunkifyWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChunkifyWithStreamedResponse:
        return AsyncChunkifyWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="repeat")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        return {**self._project_access_token, **self._team_access_token}

    @property
    def _project_access_token(self) -> dict[str, str]:
        project_access_token = self.project_access_token
        if project_access_token is None:
            return {}
        return {"Authorization": f"Bearer {project_access_token}"}

    @property
    def _team_access_token(self) -> dict[str, str]:
        team_access_token = self.team_access_token
        if team_access_token is None:
            return {}
        return {"Authorization": f"Bearer {team_access_token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    @override
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if self.project_access_token and headers.get("Authorization"):
            return
        if isinstance(custom_headers.get("Authorization"), Omit):
            return

        if self.team_access_token and headers.get("Authorization"):
            return
        if isinstance(custom_headers.get("Authorization"), Omit):
            return

        raise TypeError(
            '"Could not resolve authentication method. Expected either project_access_token or team_access_token to be set. Or for one of the `Authorization` or `Authorization` headers to be explicitly omitted"'
        )

    def copy(
        self,
        *,
        project_access_token: str | None = None,
        team_access_token: str | None = None,
        webhook_key: str | None = None,
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
            project_access_token=project_access_token or self.project_access_token,
            team_access_token=team_access_token or self.team_access_token,
            webhook_key=webhook_key or self.webhook_key,
            base_url=base_url or self.base_url,
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


class ChunkifyWithRawResponse:
    _client: Chunkify

    def __init__(self, client: Chunkify) -> None:
        self._client = client

    @cached_property
    def files(self) -> files.FilesResourceWithRawResponse:
        from .resources.files import FilesResourceWithRawResponse

        return FilesResourceWithRawResponse(self._client.files)

    @cached_property
    def jobs(self) -> jobs.JobsResourceWithRawResponse:
        from .resources.jobs import JobsResourceWithRawResponse

        return JobsResourceWithRawResponse(self._client.jobs)

    @cached_property
    def notifications(self) -> notifications.NotificationsResourceWithRawResponse:
        from .resources.notifications import NotificationsResourceWithRawResponse

        return NotificationsResourceWithRawResponse(self._client.notifications)

    @cached_property
    def projects(self) -> projects.ProjectsResourceWithRawResponse:
        from .resources.projects import ProjectsResourceWithRawResponse

        return ProjectsResourceWithRawResponse(self._client.projects)

    @cached_property
    def sources(self) -> sources.SourcesResourceWithRawResponse:
        from .resources.sources import SourcesResourceWithRawResponse

        return SourcesResourceWithRawResponse(self._client.sources)

    @cached_property
    def storages(self) -> storages.StoragesResourceWithRawResponse:
        from .resources.storages import StoragesResourceWithRawResponse

        return StoragesResourceWithRawResponse(self._client.storages)

    @cached_property
    def tokens(self) -> tokens.TokensResourceWithRawResponse:
        from .resources.tokens import TokensResourceWithRawResponse

        return TokensResourceWithRawResponse(self._client.tokens)

    @cached_property
    def uploads(self) -> uploads.UploadsResourceWithRawResponse:
        from .resources.uploads import UploadsResourceWithRawResponse

        return UploadsResourceWithRawResponse(self._client.uploads)

    @cached_property
    def webhooks(self) -> webhooks.WebhooksResourceWithRawResponse:
        from .resources.webhooks import WebhooksResourceWithRawResponse

        return WebhooksResourceWithRawResponse(self._client.webhooks)


class AsyncChunkifyWithRawResponse:
    _client: AsyncChunkify

    def __init__(self, client: AsyncChunkify) -> None:
        self._client = client

    @cached_property
    def files(self) -> files.AsyncFilesResourceWithRawResponse:
        from .resources.files import AsyncFilesResourceWithRawResponse

        return AsyncFilesResourceWithRawResponse(self._client.files)

    @cached_property
    def jobs(self) -> jobs.AsyncJobsResourceWithRawResponse:
        from .resources.jobs import AsyncJobsResourceWithRawResponse

        return AsyncJobsResourceWithRawResponse(self._client.jobs)

    @cached_property
    def notifications(self) -> notifications.AsyncNotificationsResourceWithRawResponse:
        from .resources.notifications import AsyncNotificationsResourceWithRawResponse

        return AsyncNotificationsResourceWithRawResponse(self._client.notifications)

    @cached_property
    def projects(self) -> projects.AsyncProjectsResourceWithRawResponse:
        from .resources.projects import AsyncProjectsResourceWithRawResponse

        return AsyncProjectsResourceWithRawResponse(self._client.projects)

    @cached_property
    def sources(self) -> sources.AsyncSourcesResourceWithRawResponse:
        from .resources.sources import AsyncSourcesResourceWithRawResponse

        return AsyncSourcesResourceWithRawResponse(self._client.sources)

    @cached_property
    def storages(self) -> storages.AsyncStoragesResourceWithRawResponse:
        from .resources.storages import AsyncStoragesResourceWithRawResponse

        return AsyncStoragesResourceWithRawResponse(self._client.storages)

    @cached_property
    def tokens(self) -> tokens.AsyncTokensResourceWithRawResponse:
        from .resources.tokens import AsyncTokensResourceWithRawResponse

        return AsyncTokensResourceWithRawResponse(self._client.tokens)

    @cached_property
    def uploads(self) -> uploads.AsyncUploadsResourceWithRawResponse:
        from .resources.uploads import AsyncUploadsResourceWithRawResponse

        return AsyncUploadsResourceWithRawResponse(self._client.uploads)

    @cached_property
    def webhooks(self) -> webhooks.AsyncWebhooksResourceWithRawResponse:
        from .resources.webhooks import AsyncWebhooksResourceWithRawResponse

        return AsyncWebhooksResourceWithRawResponse(self._client.webhooks)


class ChunkifyWithStreamedResponse:
    _client: Chunkify

    def __init__(self, client: Chunkify) -> None:
        self._client = client

    @cached_property
    def files(self) -> files.FilesResourceWithStreamingResponse:
        from .resources.files import FilesResourceWithStreamingResponse

        return FilesResourceWithStreamingResponse(self._client.files)

    @cached_property
    def jobs(self) -> jobs.JobsResourceWithStreamingResponse:
        from .resources.jobs import JobsResourceWithStreamingResponse

        return JobsResourceWithStreamingResponse(self._client.jobs)

    @cached_property
    def notifications(self) -> notifications.NotificationsResourceWithStreamingResponse:
        from .resources.notifications import NotificationsResourceWithStreamingResponse

        return NotificationsResourceWithStreamingResponse(self._client.notifications)

    @cached_property
    def projects(self) -> projects.ProjectsResourceWithStreamingResponse:
        from .resources.projects import ProjectsResourceWithStreamingResponse

        return ProjectsResourceWithStreamingResponse(self._client.projects)

    @cached_property
    def sources(self) -> sources.SourcesResourceWithStreamingResponse:
        from .resources.sources import SourcesResourceWithStreamingResponse

        return SourcesResourceWithStreamingResponse(self._client.sources)

    @cached_property
    def storages(self) -> storages.StoragesResourceWithStreamingResponse:
        from .resources.storages import StoragesResourceWithStreamingResponse

        return StoragesResourceWithStreamingResponse(self._client.storages)

    @cached_property
    def tokens(self) -> tokens.TokensResourceWithStreamingResponse:
        from .resources.tokens import TokensResourceWithStreamingResponse

        return TokensResourceWithStreamingResponse(self._client.tokens)

    @cached_property
    def uploads(self) -> uploads.UploadsResourceWithStreamingResponse:
        from .resources.uploads import UploadsResourceWithStreamingResponse

        return UploadsResourceWithStreamingResponse(self._client.uploads)

    @cached_property
    def webhooks(self) -> webhooks.WebhooksResourceWithStreamingResponse:
        from .resources.webhooks import WebhooksResourceWithStreamingResponse

        return WebhooksResourceWithStreamingResponse(self._client.webhooks)


class AsyncChunkifyWithStreamedResponse:
    _client: AsyncChunkify

    def __init__(self, client: AsyncChunkify) -> None:
        self._client = client

    @cached_property
    def files(self) -> files.AsyncFilesResourceWithStreamingResponse:
        from .resources.files import AsyncFilesResourceWithStreamingResponse

        return AsyncFilesResourceWithStreamingResponse(self._client.files)

    @cached_property
    def jobs(self) -> jobs.AsyncJobsResourceWithStreamingResponse:
        from .resources.jobs import AsyncJobsResourceWithStreamingResponse

        return AsyncJobsResourceWithStreamingResponse(self._client.jobs)

    @cached_property
    def notifications(self) -> notifications.AsyncNotificationsResourceWithStreamingResponse:
        from .resources.notifications import AsyncNotificationsResourceWithStreamingResponse

        return AsyncNotificationsResourceWithStreamingResponse(self._client.notifications)

    @cached_property
    def projects(self) -> projects.AsyncProjectsResourceWithStreamingResponse:
        from .resources.projects import AsyncProjectsResourceWithStreamingResponse

        return AsyncProjectsResourceWithStreamingResponse(self._client.projects)

    @cached_property
    def sources(self) -> sources.AsyncSourcesResourceWithStreamingResponse:
        from .resources.sources import AsyncSourcesResourceWithStreamingResponse

        return AsyncSourcesResourceWithStreamingResponse(self._client.sources)

    @cached_property
    def storages(self) -> storages.AsyncStoragesResourceWithStreamingResponse:
        from .resources.storages import AsyncStoragesResourceWithStreamingResponse

        return AsyncStoragesResourceWithStreamingResponse(self._client.storages)

    @cached_property
    def tokens(self) -> tokens.AsyncTokensResourceWithStreamingResponse:
        from .resources.tokens import AsyncTokensResourceWithStreamingResponse

        return AsyncTokensResourceWithStreamingResponse(self._client.tokens)

    @cached_property
    def uploads(self) -> uploads.AsyncUploadsResourceWithStreamingResponse:
        from .resources.uploads import AsyncUploadsResourceWithStreamingResponse

        return AsyncUploadsResourceWithStreamingResponse(self._client.uploads)

    @cached_property
    def webhooks(self) -> webhooks.AsyncWebhooksResourceWithStreamingResponse:
        from .resources.webhooks import AsyncWebhooksResourceWithStreamingResponse

        return AsyncWebhooksResourceWithStreamingResponse(self._client.webhooks)


Client = Chunkify

AsyncClient = AsyncChunkify
