"""
Extractor for order status inquiry intent.
"""

from typing import Optional

from pydantic import BaseModel, Field

from .base import BaseExtractor


class OrderStatusContext(BaseModel):
    """Extracted context from user's order status inquiry."""

    order_id: Optional[str] = Field(
        None,
        description="Order ID if mentioned (e.g., 'ORD-12345', '#1234', '12345')"
    )


class OrderStatusExtractor(BaseExtractor):
    """Extracts order_id from order status inquiries."""

    intent = "order_status"
    context_model = OrderStatusContext

    def get_extraction_prompt(self) -> str:
        return """Extract order ID from this customer message for status inquiry.

If the user mentions an order ID (any format like ORD-12345, #1234, order number 5678), extract it.

Only extract values that are clearly stated. Don't infer or make up missing values.
If no order ID is mentioned, leave it as null."""
