"""OpenRouter API type definitions.

OpenRouter's schema is similar to OpenAI Chat Completions but with some differences.
Reference: https://openrouter.ai/docs/api/reference/overview
"""

from typing import Literal, TypeGuard

from pydantic import BaseModel, ConfigDict, Field

type JSONPrimitive = str | int | float | bool | None
type JSONValue = JSONPrimitive | list["JSONValue"] | dict[str, "JSONValue"]
type JSONObject = dict[str, JSONValue]
type JSONArray = list[JSONValue]


class ErrorResponse(BaseModel):
    code: int
    message: str
    metadata: dict[str, JSONValue] | None = None


class FunctionCall(BaseModel):
    name: str
    arguments: str | None = None


class ToolCall(BaseModel):
    id: str
    type: Literal["function"]
    function: FunctionCall


class NonStreamingMessage(BaseModel):
    role: str
    content: str | None = None
    tool_calls: list[ToolCall] | None = None


class NonStreamingChoice(BaseModel):
    finish_reason: str | None = None
    native_finish_reason: str | None = None
    message: NonStreamingMessage | None = None
    error: ErrorResponse | None = None


class StreamingDelta(BaseModel):
    role: str | None = None
    content: str | None = None
    tool_calls: list[ToolCall] | None = None


class StreamingChoice(BaseModel):
    finish_reason: str | None = None
    native_finish_reason: str | None = None
    delta: StreamingDelta | None = None
    error: ErrorResponse | None = None


class ResponseUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion", "chat.completion.chunk"]
    created: int
    model: str
    choices: list[NonStreamingChoice | StreamingChoice] = Field(default_factory=list)
    system_fingerprint: str | None = None
    usage: ResponseUsage | None = None


class GenerationUsage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class GenerationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    model: str | None = None
    cost: float | None = None
    usage: GenerationUsage | None = None


class JSONTypeError(TypeError):
    pass


def _is_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def _is_dict(value: object) -> TypeGuard[dict[object, object]]:
    return isinstance(value, dict)


def ensure_json_value(value: object) -> JSONValue:
    """Runtime validation/conversion: `object` -> JSONValue."""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if _is_list(value):
        list_out: list[JSONValue] = []
        for v in value:
            list_out.append(ensure_json_value(v))
        return list_out
    if _is_dict(value):
        dict_out: dict[str, JSONValue] = {}
        for k, v in value.items():
            if not isinstance(k, str):
                raise JSONTypeError(
                    f"JSON object key must be str, got {type(k).__name__}"
                )
            dict_out[k] = ensure_json_value(v)
        return dict_out
    raise JSONTypeError(f"Not a JSON value: {type(value).__name__}")


def ensure_json_object(value: object) -> JSONObject:
    v = ensure_json_value(value)
    if isinstance(v, dict):
        return v
    raise JSONTypeError(f"Not a JSON object: {type(v).__name__}")
