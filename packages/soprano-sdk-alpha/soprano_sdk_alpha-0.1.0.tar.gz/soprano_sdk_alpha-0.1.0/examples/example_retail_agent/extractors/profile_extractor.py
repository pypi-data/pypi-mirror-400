"""
Extractor for profile inquiry intent.
"""

from typing import Optional

from pydantic import BaseModel, Field

from .base import BaseExtractor


class ProfileContext(BaseModel):
    """Extracted context from user's profile inquiry."""

    customer_identifier: Optional[str] = Field(
        None,
        description="Customer identifier if mentioned (email, phone, or customer ID)"
    )


class ProfileExtractor(BaseExtractor):
    """Extracts customer identifier from profile inquiries."""

    intent = "profile"
    context_model = ProfileContext

    def get_extraction_prompt(self) -> str:
        return """Extract customer identifier from this message for profile lookup.

If the user mentions:
- An email address, extract it
- A phone number, extract it
- A customer ID (like CUST-123456), extract it

Only extract values that are clearly stated. Don't infer or make up missing values.
If no identifier is mentioned, leave it as null."""
