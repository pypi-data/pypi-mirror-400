# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "IngestCreateParams",
    "Event",
    "EventIngestTrace",
    "EventIngestTraceStep",
    "EventIngestTraceStepLlmStartStep",
    "EventIngestTraceStepLlmEndStep",
    "EventIngestTraceStepLlmEndStepUsage",
    "EventIngestTraceStepToolStep",
    "EventIngestTraceStepRetrieverStep",
    "EventIngestTraceStepLogStep",
    "EventIngestTraceStepGroupStep",
    "EventIngestTraceStepResponseStep",
    "EventIngestTraceStepRequestStep",
    "EventIngestLlmStartStep",
    "EventIngestLlmEndStep",
    "EventIngestLlmEndStepUsage",
    "EventIngestToolStep",
    "EventIngestRetrieverStep",
    "EventIngestLogStep",
    "EventIngestGroupStep",
    "EventIngestResponseStep",
    "EventIngestRequestStep",
]


class IngestCreateParams(TypedDict, total=False):
    events: Required[Iterable[Event]]
    """Array of events to be ingested, which can be traces or steps."""


class EventIngestTraceStepLlmStartStep(TypedDict, total=False):
    """Start of an LLM trace."""

    id: Required[str]
    """UUID for the step."""

    event: Required[Literal["start"]]

    input: Required[str]
    """JSON input for this LLM trace event (e.g., the prompt)."""

    model_id: Required[Annotated[str, PropertyInfo(alias="modelId")]]
    """Model ID or name used for the LLM call."""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    trace_id: Required[Annotated[str, PropertyInfo(alias="traceId")]]
    """UUID referencing the parent trace's ID."""

    type: Required[Literal["llm"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object]]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[Dict[str, object], Iterable[object]]
    """Arbitrary params for the step."""


class EventIngestTraceStepLlmEndStepUsage(TypedDict, total=False):
    """Number of input and output tokens used by the LLM."""

    completion_tokens: Required[Annotated[int, PropertyInfo(alias="completionTokens")]]
    """Number of completion tokens used by the LLM."""

    prompt_tokens: Required[Annotated[int, PropertyInfo(alias="promptTokens")]]
    """Number of prompt tokens used by the LLM."""


class EventIngestTraceStepLlmEndStep(TypedDict, total=False):
    """End of an LLM trace."""

    id: Required[str]
    """UUID for the step."""

    event: Required[Literal["end"]]

    model_id: Required[Annotated[str, PropertyInfo(alias="modelId")]]
    """Model ID or name used for the LLM call."""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    trace_id: Required[Annotated[str, PropertyInfo(alias="traceId")]]
    """UUID referencing the parent trace's ID."""

    type: Required[Literal["llm"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object]]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    output: str
    """JSON describing the output.

    String inputs are parsed or wrapped in { message: val }.
    """

    params: Union[Dict[str, object], Iterable[object]]
    """Arbitrary params for the step."""

    usage: EventIngestTraceStepLlmEndStepUsage
    """Number of input and output tokens used by the LLM."""


class EventIngestTraceStepToolStep(TypedDict, total=False):
    """Track all tool calls using the Tool Step event"""

    id: Required[str]
    """UUID for the step."""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    trace_id: Required[Annotated[str, PropertyInfo(alias="traceId")]]
    """UUID referencing the parent trace's ID."""

    type: Required[Literal["tool"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object]]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[Dict[str, object], Iterable[object]]
    """Arbitrary params for the step."""

    tool_input: Annotated[str, PropertyInfo(alias="toolInput")]
    """JSON input for the tool call."""

    tool_output: Annotated[str, PropertyInfo(alias="toolOutput")]
    """JSON output from the tool call."""


class EventIngestTraceStepRetrieverStep(TypedDict, total=False):
    """Track all retriever (RAG) calls using the Retriever Step event."""

    id: Required[str]
    """UUID for the step."""

    query: Required[str]
    """Query used for RAG."""

    result: Required[str]
    """Retrieved text"""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    trace_id: Required[Annotated[str, PropertyInfo(alias="traceId")]]
    """UUID referencing the parent trace's ID."""

    type: Required[Literal["retriever"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object]]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[Dict[str, object], Iterable[object]]
    """Arbitrary params for the step."""


class EventIngestTraceStepLogStep(TypedDict, total=False):
    """Track all logs using the Log Step event."""

    id: Required[str]
    """UUID for the step."""

    content: Required[str]
    """The actual log message for this trace."""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    trace_id: Required[Annotated[str, PropertyInfo(alias="traceId")]]
    """UUID referencing the parent trace's ID."""

    type: Required[Literal["log"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object]]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[Dict[str, object], Iterable[object]]
    """Arbitrary params for the step."""


class EventIngestTraceStepGroupStep(TypedDict, total=False):
    """
    Use this to group multiple steps together, for example a log, llm start, and llm end.
    """

    id: Required[str]
    """UUID for the step."""

    key: Required[str]
    """
    A unique identifier for the grouping, which must be appended to the
    corresponding steps
    """

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    trace_id: Required[Annotated[str, PropertyInfo(alias="traceId")]]
    """UUID referencing the parent trace's ID."""

    type: Required[Literal["group"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object]]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[Dict[str, object], Iterable[object]]
    """Arbitrary params for the step."""


class EventIngestTraceStepResponseStep(TypedDict, total=False):
    """Track AI responses to users using the Response Step event."""

    id: Required[str]
    """UUID for the step."""

    content: Required[str]
    """The response content from the AI to the user."""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    trace_id: Required[Annotated[str, PropertyInfo(alias="traceId")]]
    """UUID referencing the parent trace's ID."""

    type: Required[Literal["response"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object]]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[Dict[str, object], Iterable[object]]
    """Arbitrary params for the step."""


class EventIngestTraceStepRequestStep(TypedDict, total=False):
    """Track user requests to the AI using the Request Step event."""

    id: Required[str]
    """UUID for the step."""

    content: Required[str]
    """The request content from the user to the AI."""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    trace_id: Required[Annotated[str, PropertyInfo(alias="traceId")]]
    """UUID referencing the parent trace's ID."""

    type: Required[Literal["request"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object]]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[Dict[str, object], Iterable[object]]
    """Arbitrary params for the step."""


EventIngestTraceStep: TypeAlias = Union[
    EventIngestTraceStepLlmStartStep,
    EventIngestTraceStepLlmEndStep,
    EventIngestTraceStepToolStep,
    EventIngestTraceStepRetrieverStep,
    EventIngestTraceStepLogStep,
    EventIngestTraceStepGroupStep,
    EventIngestTraceStepResponseStep,
    EventIngestTraceStepRequestStep,
]


class EventIngestTrace(TypedDict, total=False):
    """A trace grouping related steps (e.g. a user-agent interaction or conversation)."""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["trace"]]

    metadata: Union[str, Dict[str, object], Iterable[object]]
    """Arbitrary metadata for this trace (e.g., userId, source, etc.)."""

    reference_id: Annotated[str, PropertyInfo(alias="referenceId")]
    """
    An optional reference ID to link the trace to an existing conversation or
    interaction in your own database.
    """

    steps: Iterable[EventIngestTraceStep]
    """The steps associated with the trace."""

    test_id: Annotated[str, PropertyInfo(alias="testId")]
    """The associated Test if this was triggered by an Avido eval"""


class EventIngestLlmStartStep(TypedDict, total=False):
    """Start of an LLM trace."""

    event: Required[Literal["start"]]

    input: Required[Union[str, Dict[str, object], Iterable[object]]]
    """The input for the LLM step."""

    model_id: Required[Annotated[str, PropertyInfo(alias="modelId")]]
    """Model ID or name used for the LLM call."""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["llm"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object], str]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[Dict[str, object], Iterable[object], str]
    """Arbitrary params for the step."""

    trace_id: Annotated[str, PropertyInfo(alias="traceId")]
    """The trace ID (UUID)."""


class EventIngestLlmEndStepUsage(TypedDict, total=False):
    """Number of input and output tokens used by the LLM."""

    completion_tokens: Required[Annotated[int, PropertyInfo(alias="completionTokens")]]
    """Number of completion tokens used by the LLM."""

    prompt_tokens: Required[Annotated[int, PropertyInfo(alias="promptTokens")]]
    """Number of prompt tokens used by the LLM."""


class EventIngestLlmEndStep(TypedDict, total=False):
    """End of an LLM trace."""

    event: Required[Literal["end"]]

    model_id: Required[Annotated[str, PropertyInfo(alias="modelId")]]
    """Model ID or name used for the LLM call."""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["llm"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object], str]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    output: Union[str, Dict[str, object], Iterable[object]]
    """The output for the LLM step."""

    params: Union[Dict[str, object], Iterable[object], str]
    """Arbitrary params for the step."""

    trace_id: Annotated[str, PropertyInfo(alias="traceId")]
    """The trace ID (UUID)."""

    usage: EventIngestLlmEndStepUsage
    """Number of input and output tokens used by the LLM."""


class EventIngestToolStep(TypedDict, total=False):
    """Track all tool calls using the Tool Step event"""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["tool"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object], str]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[Dict[str, object], Iterable[object], str]
    """Arbitrary params for the step."""

    tool_input: Annotated[Union[str, Dict[str, object], Iterable[object]], PropertyInfo(alias="toolInput")]
    """The input for the tool step."""

    tool_output: Annotated[Union[str, Dict[str, object], Iterable[object]], PropertyInfo(alias="toolOutput")]
    """The output for the tool step."""

    trace_id: Annotated[str, PropertyInfo(alias="traceId")]
    """The trace ID (UUID)."""


class EventIngestRetrieverStep(TypedDict, total=False):
    """Track all retriever (RAG) calls using the Retriever Step event."""

    query: Required[Union[str, Dict[str, object], Iterable[object]]]
    """The query for the retriever step."""

    result: Required[Union[str, Dict[str, object], Iterable[object]]]
    """The result for the retriever step."""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["retriever"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object], str]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[str, Dict[str, object], Iterable[object]]
    """Arbitrary params for the step."""

    trace_id: Annotated[str, PropertyInfo(alias="traceId")]
    """The trace ID (UUID)."""


class EventIngestLogStep(TypedDict, total=False):
    """Track all logs using the Log Step event."""

    content: Required[str]
    """The actual log message for this trace."""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["log"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object], str]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[Dict[str, object], Iterable[object], str]
    """Arbitrary params for the step."""

    trace_id: Annotated[str, PropertyInfo(alias="traceId")]
    """The trace ID (UUID)."""


class EventIngestGroupStep(TypedDict, total=False):
    """
    Use this to group multiple steps together, for example a log, llm start, and llm end.
    """

    key: Required[str]
    """
    A unique identifier for the grouping, which must be appended to the
    corresponding steps
    """

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["group"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object], str]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[Dict[str, object], Iterable[object], str]
    """Arbitrary params for the step."""

    trace_id: Annotated[str, PropertyInfo(alias="traceId")]
    """The trace ID (UUID)."""


class EventIngestResponseStep(TypedDict, total=False):
    """Track AI responses to users using the Response Step event."""

    content: Required[Union[str, Dict[str, object], Iterable[object]]]
    """The response content from the AI to the user."""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["response"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object], str]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[Dict[str, object], Iterable[object], str]
    """Arbitrary params for the step."""

    trace_id: Annotated[str, PropertyInfo(alias="traceId")]
    """The trace ID (UUID)."""


class EventIngestRequestStep(TypedDict, total=False):
    """Track user requests to the AI using the Request Step event."""

    content: Required[Union[str, Dict[str, object], Iterable[object]]]
    """The request content from the user to the AI."""

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["request"]]

    group: str
    """Optionally, the key for a group step to group the step with."""

    metadata: Union[Dict[str, object], Iterable[object], str]
    """Extra metadata about this trace event.

    String values are parsed as JSON if possible, otherwise wrapped in { raw: val }.
    """

    name: str
    """The name of the step."""

    params: Union[Dict[str, object], Iterable[object], str]
    """Arbitrary params for the step."""

    trace_id: Annotated[str, PropertyInfo(alias="traceId")]
    """The trace ID (UUID)."""


Event: TypeAlias = Union[
    EventIngestTrace,
    EventIngestLlmStartStep,
    EventIngestLlmEndStep,
    EventIngestToolStep,
    EventIngestRetrieverStep,
    EventIngestLogStep,
    EventIngestGroupStep,
    EventIngestResponseStep,
    EventIngestRequestStep,
]
