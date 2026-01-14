"""
Extractor for return/refund intent.
"""

from typing import Optional

from pydantic import BaseModel, Field

from .base import BaseExtractor


class ReturnRequestContext(BaseModel):
    """Extracted context from user's return request."""

    order_id: Optional[str] = Field(
        None,
        description="Order ID if mentioned (e.g., 'ORD-12345', '#1234', '12345')"
    )
    return_reason: Optional[str] = Field(
        None,
        description="Return reason if mentioned (e.g., 'damaged', 'wrong size', 'defective')"
    )


class ReturnExtractor(BaseExtractor):
    """Extracts order_id and return_reason from return requests."""

    intent = "return"
    context_model = ReturnRequestContext

    def get_extraction_prompt(self) -> str:
        return """Extract any return-related information from this customer message.

If the user mentions:
- An order ID (any format like ORD-12345, #1234, order number 5678), extract it
- A return reason (damaged, wrong size, defective, changed mind, etc.), extract it

Only extract values that are clearly stated. Don't infer or make up missing values.
If no order ID is mentioned, leave it as null.
If no reason is mentioned, leave it as null."""
