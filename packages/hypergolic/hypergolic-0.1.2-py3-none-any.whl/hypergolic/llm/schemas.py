from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

from .enums import StopReason
from ..tools.enums import ToolName


class CacheControl(BaseModel):
    type: Literal["ephemeral"] = "ephemeral"


class UserToolResult(BaseModel):
    type: Literal["tool_result"] = Field(default="tool_result")
    tool_use_id: str
    content: Union[str, list[str]]
    cache_control: Optional[CacheControl] = None


UserMessageContent = Union[str, list[UserToolResult]]


class UserMessage(BaseModel):
    role: Literal["user"] = Field(default="user")
    content: UserMessageContent


class AssistantMessageTextContent(BaseModel):
    type: Literal["text"]
    text: str
    cache_control: Optional[CacheControl] = None


class AssistantMessageToolUseContent(BaseModel):
    type: Literal["tool_use"]
    id: str
    name: ToolName
    input: dict


AssistantMessageContent = Union[
    AssistantMessageTextContent, AssistantMessageToolUseContent
]


class AssistantMessage(BaseModel):
    role: Literal["assistant"] = Field(default="assistant")
    content: list[AssistantMessageContent]


Message = Union[UserMessage, AssistantMessage]


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: Optional[int] = None
    cache_read_input_tokens: Optional[int] = None
    service_tier: Optional[str] = None


class APIResponse(BaseModel):
    id: str
    content: list[AssistantMessageContent]
    model: str
    role: str
    stop_reason: StopReason
    type: str = Field(examples=["message"])
    usage: Usage
