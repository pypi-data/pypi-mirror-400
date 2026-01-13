"""Type definitions for Perf SDK using Pydantic."""

from typing import List, Optional, Union, Literal, Dict, Any
from pydantic import BaseModel, Field


# ============================================
# Message Types
# ============================================

class TextContent(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ImageUrlDetail(BaseModel):
    url: str
    detail: Optional[Literal["low", "high", "auto"]] = None


class ImageUrlContent(BaseModel):
    type: Literal["image_url"] = "image_url"
    image_url: ImageUrlDetail


ContentPart = Union[TextContent, ImageUrlContent]


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: Union[str, List[ContentPart]]
    name: Optional[str] = None


# ============================================
# Request Types
# ============================================

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    stream: bool = False
    max_cost_per_call: Optional[float] = None
    metadata: Optional[Dict[str, str]] = None


# ============================================
# Response Types
# ============================================

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class PerfMetadata(BaseModel):
    request_id: str
    task_type: str
    complexity: float
    model_selected: str
    model_used: str
    cost_usd: float
    latency_ms: int
    fallback_used: bool
    validation_passed: bool


class ResponseMessage(BaseModel):
    role: Literal["assistant"]
    content: str


class Choice(BaseModel):
    index: int
    message: ResponseMessage
    finish_reason: Optional[Literal["stop", "length", "content_filter"]] = None


class ChatResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Usage
    perf: PerfMetadata


# ============================================
# Streaming Types
# ============================================

class DeltaContent(BaseModel):
    role: Optional[Literal["assistant"]] = None
    content: Optional[str] = None


class StreamChoice(BaseModel):
    index: int
    delta: DeltaContent
    finish_reason: Optional[Literal["stop", "length"]] = None


class ChatStreamChunk(BaseModel):
    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamChoice]
