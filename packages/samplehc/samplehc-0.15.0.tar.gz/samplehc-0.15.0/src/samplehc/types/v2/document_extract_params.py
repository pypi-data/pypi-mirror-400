# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo

__all__ = [
    "DocumentExtractParams",
    "Document",
    "OcrEnhance",
    "OcrEnhanceAgentic",
    "OcrEnhanceAgenticUnionMember0",
    "OcrEnhanceAgenticUnionMember1",
]


class DocumentExtractParams(TypedDict, total=False):
    documents: Required[Iterable[Document]]
    """An array of documents to extract data from."""

    prompt: Required[str]
    """A prompt guiding the extraction process."""

    response_json_schema: Required[Annotated[Dict[str, object], PropertyInfo(alias="responseJsonSchema")]]
    """A JSON schema defining the structure of the desired extraction output."""

    model: Literal["reasoning-3-mini", "reasoning-3", "base-5", "base-5-mini", "base-5-nano"]
    """The model to use for extraction."""

    ocr_enhance: Annotated[OcrEnhance, PropertyInfo(alias="ocrEnhance")]
    """OCR enhancement configuration for figure and text analysis."""

    priority: Literal["interactive", "non-interactive"]
    """The priority of the extraction task. Non-interactive is lower priority."""

    reasoning_effort: Annotated[Literal["low", "medium", "high"], PropertyInfo(alias="reasoningEffort")]
    """Optional control over the reasoning effort for extraction."""


class Document(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]


class OcrEnhanceAgenticUnionMember0(TypedDict, total=False):
    prompt: Required[str]
    """Prompt for figure analysis."""

    scope: Required[Literal["figure"]]


class OcrEnhanceAgenticUnionMember1(TypedDict, total=False):
    scope: Required[Literal["text"]]

    prompt: str
    """Optional prompt for text analysis."""


OcrEnhanceAgentic: TypeAlias = Union[OcrEnhanceAgenticUnionMember0, OcrEnhanceAgenticUnionMember1]


class OcrEnhance(TypedDict, total=False):
    """OCR enhancement configuration for figure and text analysis."""

    agentic: Required[Iterable[OcrEnhanceAgentic]]
    """Agentic enhancement configuration."""

    summarize_figures: Required[Annotated[bool, PropertyInfo(alias="summarizeFigures")]]
    """Whether to summarize figures during OCR."""
