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
from ._exceptions import AvidoError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import (
        runs,
        tasks,
        tests,
        ingest,
        topics,
        traces,
        documents,
        annotations,
        applications,
        style_guides,
        validate_webhook,
    )
    from .resources.runs import RunsResource, AsyncRunsResource
    from .resources.tasks import TasksResource, AsyncTasksResource
    from .resources.tests import TestsResource, AsyncTestsResource
    from .resources.ingest import IngestResource, AsyncIngestResource
    from .resources.topics import TopicsResource, AsyncTopicsResource
    from .resources.traces import TracesResource, AsyncTracesResource
    from .resources.documents import DocumentsResource, AsyncDocumentsResource
    from .resources.annotations import AnnotationsResource, AsyncAnnotationsResource
    from .resources.applications import ApplicationsResource, AsyncApplicationsResource
    from .resources.style_guides import StyleGuidesResource, AsyncStyleGuidesResource
    from .resources.validate_webhook import ValidateWebhookResource, AsyncValidateWebhookResource

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "Avido", "AsyncAvido", "Client", "AsyncClient"]


class Avido(SyncAPIClient):
    # client options
    api_key: str
    application_id: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        application_id: str | None = None,
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
        """Construct a new synchronous Avido client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `AVIDO_API_KEY`
        - `application_id` from `AVIDO_APPLICATION_ID`
        """
        if api_key is None:
            api_key = os.environ.get("AVIDO_API_KEY")
        if api_key is None:
            raise AvidoError(
                "The api_key client option must be set either by passing api_key to the client or by setting the AVIDO_API_KEY environment variable"
            )
        self.api_key = api_key

        if application_id is None:
            application_id = os.environ.get("AVIDO_APPLICATION_ID")
        if application_id is None:
            raise AvidoError(
                "The application_id client option must be set either by passing application_id to the client or by setting the AVIDO_APPLICATION_ID environment variable"
            )
        self.application_id = application_id

        if base_url is None:
            base_url = os.environ.get("AVIDO_BASE_URL")
        if base_url is None:
            base_url = f"https://api.avidoai.com"

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
    def validate_webhook(self) -> ValidateWebhookResource:
        from .resources.validate_webhook import ValidateWebhookResource

        return ValidateWebhookResource(self)

    @cached_property
    def applications(self) -> ApplicationsResource:
        from .resources.applications import ApplicationsResource

        return ApplicationsResource(self)

    @cached_property
    def traces(self) -> TracesResource:
        from .resources.traces import TracesResource

        return TracesResource(self)

    @cached_property
    def ingest(self) -> IngestResource:
        from .resources.ingest import IngestResource

        return IngestResource(self)

    @cached_property
    def tasks(self) -> TasksResource:
        from .resources.tasks import TasksResource

        return TasksResource(self)

    @cached_property
    def tests(self) -> TestsResource:
        from .resources.tests import TestsResource

        return TestsResource(self)

    @cached_property
    def topics(self) -> TopicsResource:
        from .resources.topics import TopicsResource

        return TopicsResource(self)

    @cached_property
    def annotations(self) -> AnnotationsResource:
        from .resources.annotations import AnnotationsResource

        return AnnotationsResource(self)

    @cached_property
    def runs(self) -> RunsResource:
        from .resources.runs import RunsResource

        return RunsResource(self)

    @cached_property
    def style_guides(self) -> StyleGuidesResource:
        from .resources.style_guides import StyleGuidesResource

        return StyleGuidesResource(self)

    @cached_property
    def documents(self) -> DocumentsResource:
        from .resources.documents import DocumentsResource

        return DocumentsResource(self)

    @cached_property
    def with_raw_response(self) -> AvidoWithRawResponse:
        return AvidoWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AvidoWithStreamedResponse:
        return AvidoWithStreamedResponse(self)

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
            "x-application-id": self.application_id,
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        application_id: str | None = None,
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
            application_id=application_id or self.application_id,
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


class AsyncAvido(AsyncAPIClient):
    # client options
    api_key: str
    application_id: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        application_id: str | None = None,
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
        """Construct a new async AsyncAvido client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `AVIDO_API_KEY`
        - `application_id` from `AVIDO_APPLICATION_ID`
        """
        if api_key is None:
            api_key = os.environ.get("AVIDO_API_KEY")
        if api_key is None:
            raise AvidoError(
                "The api_key client option must be set either by passing api_key to the client or by setting the AVIDO_API_KEY environment variable"
            )
        self.api_key = api_key

        if application_id is None:
            application_id = os.environ.get("AVIDO_APPLICATION_ID")
        if application_id is None:
            raise AvidoError(
                "The application_id client option must be set either by passing application_id to the client or by setting the AVIDO_APPLICATION_ID environment variable"
            )
        self.application_id = application_id

        if base_url is None:
            base_url = os.environ.get("AVIDO_BASE_URL")
        if base_url is None:
            base_url = f"https://api.avidoai.com"

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
    def validate_webhook(self) -> AsyncValidateWebhookResource:
        from .resources.validate_webhook import AsyncValidateWebhookResource

        return AsyncValidateWebhookResource(self)

    @cached_property
    def applications(self) -> AsyncApplicationsResource:
        from .resources.applications import AsyncApplicationsResource

        return AsyncApplicationsResource(self)

    @cached_property
    def traces(self) -> AsyncTracesResource:
        from .resources.traces import AsyncTracesResource

        return AsyncTracesResource(self)

    @cached_property
    def ingest(self) -> AsyncIngestResource:
        from .resources.ingest import AsyncIngestResource

        return AsyncIngestResource(self)

    @cached_property
    def tasks(self) -> AsyncTasksResource:
        from .resources.tasks import AsyncTasksResource

        return AsyncTasksResource(self)

    @cached_property
    def tests(self) -> AsyncTestsResource:
        from .resources.tests import AsyncTestsResource

        return AsyncTestsResource(self)

    @cached_property
    def topics(self) -> AsyncTopicsResource:
        from .resources.topics import AsyncTopicsResource

        return AsyncTopicsResource(self)

    @cached_property
    def annotations(self) -> AsyncAnnotationsResource:
        from .resources.annotations import AsyncAnnotationsResource

        return AsyncAnnotationsResource(self)

    @cached_property
    def runs(self) -> AsyncRunsResource:
        from .resources.runs import AsyncRunsResource

        return AsyncRunsResource(self)

    @cached_property
    def style_guides(self) -> AsyncStyleGuidesResource:
        from .resources.style_guides import AsyncStyleGuidesResource

        return AsyncStyleGuidesResource(self)

    @cached_property
    def documents(self) -> AsyncDocumentsResource:
        from .resources.documents import AsyncDocumentsResource

        return AsyncDocumentsResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncAvidoWithRawResponse:
        return AsyncAvidoWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAvidoWithStreamedResponse:
        return AsyncAvidoWithStreamedResponse(self)

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
            "x-application-id": self.application_id,
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        application_id: str | None = None,
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
            application_id=application_id or self.application_id,
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


class AvidoWithRawResponse:
    _client: Avido

    def __init__(self, client: Avido) -> None:
        self._client = client

    @cached_property
    def validate_webhook(self) -> validate_webhook.ValidateWebhookResourceWithRawResponse:
        from .resources.validate_webhook import ValidateWebhookResourceWithRawResponse

        return ValidateWebhookResourceWithRawResponse(self._client.validate_webhook)

    @cached_property
    def applications(self) -> applications.ApplicationsResourceWithRawResponse:
        from .resources.applications import ApplicationsResourceWithRawResponse

        return ApplicationsResourceWithRawResponse(self._client.applications)

    @cached_property
    def traces(self) -> traces.TracesResourceWithRawResponse:
        from .resources.traces import TracesResourceWithRawResponse

        return TracesResourceWithRawResponse(self._client.traces)

    @cached_property
    def ingest(self) -> ingest.IngestResourceWithRawResponse:
        from .resources.ingest import IngestResourceWithRawResponse

        return IngestResourceWithRawResponse(self._client.ingest)

    @cached_property
    def tasks(self) -> tasks.TasksResourceWithRawResponse:
        from .resources.tasks import TasksResourceWithRawResponse

        return TasksResourceWithRawResponse(self._client.tasks)

    @cached_property
    def tests(self) -> tests.TestsResourceWithRawResponse:
        from .resources.tests import TestsResourceWithRawResponse

        return TestsResourceWithRawResponse(self._client.tests)

    @cached_property
    def topics(self) -> topics.TopicsResourceWithRawResponse:
        from .resources.topics import TopicsResourceWithRawResponse

        return TopicsResourceWithRawResponse(self._client.topics)

    @cached_property
    def annotations(self) -> annotations.AnnotationsResourceWithRawResponse:
        from .resources.annotations import AnnotationsResourceWithRawResponse

        return AnnotationsResourceWithRawResponse(self._client.annotations)

    @cached_property
    def runs(self) -> runs.RunsResourceWithRawResponse:
        from .resources.runs import RunsResourceWithRawResponse

        return RunsResourceWithRawResponse(self._client.runs)

    @cached_property
    def style_guides(self) -> style_guides.StyleGuidesResourceWithRawResponse:
        from .resources.style_guides import StyleGuidesResourceWithRawResponse

        return StyleGuidesResourceWithRawResponse(self._client.style_guides)

    @cached_property
    def documents(self) -> documents.DocumentsResourceWithRawResponse:
        from .resources.documents import DocumentsResourceWithRawResponse

        return DocumentsResourceWithRawResponse(self._client.documents)


class AsyncAvidoWithRawResponse:
    _client: AsyncAvido

    def __init__(self, client: AsyncAvido) -> None:
        self._client = client

    @cached_property
    def validate_webhook(self) -> validate_webhook.AsyncValidateWebhookResourceWithRawResponse:
        from .resources.validate_webhook import AsyncValidateWebhookResourceWithRawResponse

        return AsyncValidateWebhookResourceWithRawResponse(self._client.validate_webhook)

    @cached_property
    def applications(self) -> applications.AsyncApplicationsResourceWithRawResponse:
        from .resources.applications import AsyncApplicationsResourceWithRawResponse

        return AsyncApplicationsResourceWithRawResponse(self._client.applications)

    @cached_property
    def traces(self) -> traces.AsyncTracesResourceWithRawResponse:
        from .resources.traces import AsyncTracesResourceWithRawResponse

        return AsyncTracesResourceWithRawResponse(self._client.traces)

    @cached_property
    def ingest(self) -> ingest.AsyncIngestResourceWithRawResponse:
        from .resources.ingest import AsyncIngestResourceWithRawResponse

        return AsyncIngestResourceWithRawResponse(self._client.ingest)

    @cached_property
    def tasks(self) -> tasks.AsyncTasksResourceWithRawResponse:
        from .resources.tasks import AsyncTasksResourceWithRawResponse

        return AsyncTasksResourceWithRawResponse(self._client.tasks)

    @cached_property
    def tests(self) -> tests.AsyncTestsResourceWithRawResponse:
        from .resources.tests import AsyncTestsResourceWithRawResponse

        return AsyncTestsResourceWithRawResponse(self._client.tests)

    @cached_property
    def topics(self) -> topics.AsyncTopicsResourceWithRawResponse:
        from .resources.topics import AsyncTopicsResourceWithRawResponse

        return AsyncTopicsResourceWithRawResponse(self._client.topics)

    @cached_property
    def annotations(self) -> annotations.AsyncAnnotationsResourceWithRawResponse:
        from .resources.annotations import AsyncAnnotationsResourceWithRawResponse

        return AsyncAnnotationsResourceWithRawResponse(self._client.annotations)

    @cached_property
    def runs(self) -> runs.AsyncRunsResourceWithRawResponse:
        from .resources.runs import AsyncRunsResourceWithRawResponse

        return AsyncRunsResourceWithRawResponse(self._client.runs)

    @cached_property
    def style_guides(self) -> style_guides.AsyncStyleGuidesResourceWithRawResponse:
        from .resources.style_guides import AsyncStyleGuidesResourceWithRawResponse

        return AsyncStyleGuidesResourceWithRawResponse(self._client.style_guides)

    @cached_property
    def documents(self) -> documents.AsyncDocumentsResourceWithRawResponse:
        from .resources.documents import AsyncDocumentsResourceWithRawResponse

        return AsyncDocumentsResourceWithRawResponse(self._client.documents)


class AvidoWithStreamedResponse:
    _client: Avido

    def __init__(self, client: Avido) -> None:
        self._client = client

    @cached_property
    def validate_webhook(self) -> validate_webhook.ValidateWebhookResourceWithStreamingResponse:
        from .resources.validate_webhook import ValidateWebhookResourceWithStreamingResponse

        return ValidateWebhookResourceWithStreamingResponse(self._client.validate_webhook)

    @cached_property
    def applications(self) -> applications.ApplicationsResourceWithStreamingResponse:
        from .resources.applications import ApplicationsResourceWithStreamingResponse

        return ApplicationsResourceWithStreamingResponse(self._client.applications)

    @cached_property
    def traces(self) -> traces.TracesResourceWithStreamingResponse:
        from .resources.traces import TracesResourceWithStreamingResponse

        return TracesResourceWithStreamingResponse(self._client.traces)

    @cached_property
    def ingest(self) -> ingest.IngestResourceWithStreamingResponse:
        from .resources.ingest import IngestResourceWithStreamingResponse

        return IngestResourceWithStreamingResponse(self._client.ingest)

    @cached_property
    def tasks(self) -> tasks.TasksResourceWithStreamingResponse:
        from .resources.tasks import TasksResourceWithStreamingResponse

        return TasksResourceWithStreamingResponse(self._client.tasks)

    @cached_property
    def tests(self) -> tests.TestsResourceWithStreamingResponse:
        from .resources.tests import TestsResourceWithStreamingResponse

        return TestsResourceWithStreamingResponse(self._client.tests)

    @cached_property
    def topics(self) -> topics.TopicsResourceWithStreamingResponse:
        from .resources.topics import TopicsResourceWithStreamingResponse

        return TopicsResourceWithStreamingResponse(self._client.topics)

    @cached_property
    def annotations(self) -> annotations.AnnotationsResourceWithStreamingResponse:
        from .resources.annotations import AnnotationsResourceWithStreamingResponse

        return AnnotationsResourceWithStreamingResponse(self._client.annotations)

    @cached_property
    def runs(self) -> runs.RunsResourceWithStreamingResponse:
        from .resources.runs import RunsResourceWithStreamingResponse

        return RunsResourceWithStreamingResponse(self._client.runs)

    @cached_property
    def style_guides(self) -> style_guides.StyleGuidesResourceWithStreamingResponse:
        from .resources.style_guides import StyleGuidesResourceWithStreamingResponse

        return StyleGuidesResourceWithStreamingResponse(self._client.style_guides)

    @cached_property
    def documents(self) -> documents.DocumentsResourceWithStreamingResponse:
        from .resources.documents import DocumentsResourceWithStreamingResponse

        return DocumentsResourceWithStreamingResponse(self._client.documents)


class AsyncAvidoWithStreamedResponse:
    _client: AsyncAvido

    def __init__(self, client: AsyncAvido) -> None:
        self._client = client

    @cached_property
    def validate_webhook(self) -> validate_webhook.AsyncValidateWebhookResourceWithStreamingResponse:
        from .resources.validate_webhook import AsyncValidateWebhookResourceWithStreamingResponse

        return AsyncValidateWebhookResourceWithStreamingResponse(self._client.validate_webhook)

    @cached_property
    def applications(self) -> applications.AsyncApplicationsResourceWithStreamingResponse:
        from .resources.applications import AsyncApplicationsResourceWithStreamingResponse

        return AsyncApplicationsResourceWithStreamingResponse(self._client.applications)

    @cached_property
    def traces(self) -> traces.AsyncTracesResourceWithStreamingResponse:
        from .resources.traces import AsyncTracesResourceWithStreamingResponse

        return AsyncTracesResourceWithStreamingResponse(self._client.traces)

    @cached_property
    def ingest(self) -> ingest.AsyncIngestResourceWithStreamingResponse:
        from .resources.ingest import AsyncIngestResourceWithStreamingResponse

        return AsyncIngestResourceWithStreamingResponse(self._client.ingest)

    @cached_property
    def tasks(self) -> tasks.AsyncTasksResourceWithStreamingResponse:
        from .resources.tasks import AsyncTasksResourceWithStreamingResponse

        return AsyncTasksResourceWithStreamingResponse(self._client.tasks)

    @cached_property
    def tests(self) -> tests.AsyncTestsResourceWithStreamingResponse:
        from .resources.tests import AsyncTestsResourceWithStreamingResponse

        return AsyncTestsResourceWithStreamingResponse(self._client.tests)

    @cached_property
    def topics(self) -> topics.AsyncTopicsResourceWithStreamingResponse:
        from .resources.topics import AsyncTopicsResourceWithStreamingResponse

        return AsyncTopicsResourceWithStreamingResponse(self._client.topics)

    @cached_property
    def annotations(self) -> annotations.AsyncAnnotationsResourceWithStreamingResponse:
        from .resources.annotations import AsyncAnnotationsResourceWithStreamingResponse

        return AsyncAnnotationsResourceWithStreamingResponse(self._client.annotations)

    @cached_property
    def runs(self) -> runs.AsyncRunsResourceWithStreamingResponse:
        from .resources.runs import AsyncRunsResourceWithStreamingResponse

        return AsyncRunsResourceWithStreamingResponse(self._client.runs)

    @cached_property
    def style_guides(self) -> style_guides.AsyncStyleGuidesResourceWithStreamingResponse:
        from .resources.style_guides import AsyncStyleGuidesResourceWithStreamingResponse

        return AsyncStyleGuidesResourceWithStreamingResponse(self._client.style_guides)

    @cached_property
    def documents(self) -> documents.AsyncDocumentsResourceWithStreamingResponse:
        from .resources.documents import AsyncDocumentsResourceWithStreamingResponse

        return AsyncDocumentsResourceWithStreamingResponse(self._client.documents)


Client = Avido

AsyncClient = AsyncAvido
