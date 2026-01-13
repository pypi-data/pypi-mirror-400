"""Pydantic models for LLM output and transformer result."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class FormatType(str, Enum):
    """WhatsApp message format types."""

    PLAIN_TEXT = "plain_text"
    QUICK_REPLY = "quick_reply"
    LIST = "list"


class Option(BaseModel):
    """A single option/choice for the user."""

    title: str = Field(..., min_length=1, description="Short label for the option")
    description: str | None = Field(
        None, description="Additional detail (used in list format)"
    )


class Section(BaseModel):
    """A group of related options."""

    title: str = Field(..., min_length=1, description="Category name")
    options: list[Option] = Field(..., min_length=1, description="Options in section")


class LLMOutput(BaseModel):
    """Intermediate format from LLM to be transformed to WhatsApp JSON."""

    body: str = Field(..., min_length=1, description="Main response text")
    options: list[Option] | None = Field(
        None, description="Flat list of options (mutually exclusive with sections)"
    )
    sections: list[Section] | None = Field(
        None, description="Grouped options (mutually exclusive with options)"
    )
    header: str | None = Field(None, description="Short header text")
    footer: str | None = Field(None, description="Disclaimer or additional info")

    @model_validator(mode="after")
    def validate_options_or_sections(self) -> "LLMOutput":
        """Ensure options and sections are mutually exclusive."""
        if self.options and self.sections:
            raise ValueError("Cannot have both 'options' and 'sections'")
        return self


class TransformResult(BaseModel):
    """Result of transforming LLM output to WhatsApp JSON."""

    success: bool = Field(True, description="Always true unless catastrophic error")
    whatsapp_json: dict[str, Any] = Field(
        ..., description="Valid WhatsApp Business API message payload"
    )
    format_used: FormatType = Field(..., description="Format that was selected")
    fallback_used: bool = Field(
        False, description="True if format was downgraded due to constraints"
    )
    fallback_reason: str | None = Field(
        None, description="Reason for fallback (if applicable)"
    )
    modifications: list[str] = Field(
        default_factory=list, description="List of modifications applied"
    )


# WhatsApp constraints as constants
class Constraints:
    """WhatsApp Business API constraints."""

    # Quick Reply Buttons
    QUICK_REPLY_MAX_BUTTONS = 3
    QUICK_REPLY_BUTTON_TITLE_MAX = 20
    QUICK_REPLY_BUTTON_ID_MAX = 256

    # List Messages
    LIST_MAX_SECTIONS = 10
    LIST_MAX_ROWS = 10
    LIST_ROW_TITLE_MAX = 24
    LIST_ROW_DESCRIPTION_MAX = 72
    LIST_ROW_ID_MAX = 200
    LIST_BUTTON_TEXT_MAX = 20
    LIST_SECTION_TITLE_MAX = 24

    # Common
    BODY_MAX = 1024
    HEADER_MAX = 60
    FOOTER_MAX = 60

    # Plain Text
    PLAIN_TEXT_BODY_MAX = 1600

    # Default values
    DEFAULT_LIST_BUTTON_TEXT = "Select Option"
