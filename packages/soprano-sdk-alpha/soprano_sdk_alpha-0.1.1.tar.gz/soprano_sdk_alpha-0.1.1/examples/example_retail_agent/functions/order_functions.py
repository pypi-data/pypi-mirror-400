"""
Business logic functions for order status inquiry workflow.

Each function receives the full workflow state dict and returns a result.
These are mock implementations for demonstration purposes.
"""

from datetime import datetime, timedelta


def lookup_order_status(state: dict) -> dict:
    """
    Look up order status by order ID.

    In production, this would:
    - Query order database
    - Get shipping carrier tracking info
    - Calculate estimated delivery

    Args:
        state: Workflow state containing order_id

    Returns:
        dict with "found" key for routing, plus status details
    """
    order_id = state.get("order_id", "")

    # Mock logic based on last digit of order ID
    if not order_id:
        print("[lookup_order_status] No order ID provided")
        return {"found": False}

    last_digit = order_id[-1] if order_id else "0"

    # Orders ending in 9: not found
    if last_digit == "9":
        print(f"[lookup_order_status] Order {order_id} NOT FOUND")
        return {"found": False}

    # Orders ending in 1: delivered
    if last_digit == "1":
        delivered_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        print(f"[lookup_order_status] Order {order_id} DELIVERED on {delivered_date}")
        return {
            "found": True,
            "status": "delivered",
            "shipped_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "delivered_date": delivered_date,
            "tracking_number": f"1Z999AA1{order_id[-4:].zfill(4)}",
            "carrier": "UPS",
        }

    # Orders ending in 2: shipped (in transit)
    if last_digit == "2":
        shipped_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        eta = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        print(f"[lookup_order_status] Order {order_id} SHIPPED, ETA: {eta}")
        return {
            "found": True,
            "status": "shipped",
            "shipped_date": shipped_date,
            "estimated_delivery": eta,
            "tracking_number": f"1Z999AA2{order_id[-4:].zfill(4)}",
            "carrier": "UPS",
            "last_location": "Distribution Center, Chicago IL",
        }

    # All other orders: processing
    order_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    eta = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    print(f"[lookup_order_status] Order {order_id} PROCESSING, ETA: {eta}")
    return {
        "found": True,
        "status": "processing",
        "order_date": order_date,
        "estimated_ship_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "estimated_delivery": eta,
    }
