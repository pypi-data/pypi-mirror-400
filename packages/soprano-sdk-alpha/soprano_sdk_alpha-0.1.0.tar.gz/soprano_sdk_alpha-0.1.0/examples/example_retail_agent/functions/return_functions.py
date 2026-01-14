"""
Business logic functions for retail return processing workflow.

Each function receives the full workflow state dict and returns a result.
These are mock implementations for demonstration purposes.
"""


def check_eligibility(state: dict) -> bool:
    """
    Check if an order is eligible for return.

    In production, this would:
    - Query order database
    - Check return window (e.g., 30 days)
    - Verify item category allows returns
    - Check if not already returned

    Args:
        state: Workflow state containing order_id

    Returns:
        True if eligible, False otherwise
    """
    order_id = state.get('order_id', '')

    # Mock logic: Orders ending in 0 are ineligible (for demo purposes)
    # This lets users test both eligible and ineligible paths
    if order_id and order_id[-1] == '0':
        print(f"[check_eligibility] Order {order_id} is NOT eligible (ends in 0)")
        return False

    print(f"[check_eligibility] Order {order_id} is eligible for return")
    return True


def validate_reason(state: dict) -> bool:
    """
    Validate if a return reason is acceptable per policy.
    (Synchronous version - used internally by async validation)

    Args:
        state: Workflow state containing return_reason

    Returns:
        True if valid reason, False otherwise
    """
    reason = state.get('return_reason', '').lower()

    # Invalid/suspicious reasons that are not acceptable
    invalid_patterns = [
        "just because",
        "no reason",
        "dont want",
        "don't want",
        "testing",
        "fraud",
        "free stuff"
    ]

    for pattern in invalid_patterns:
        if pattern in reason:
            print(f"[validate_reason] Reason '{reason}' is INVALID (contains '{pattern}')")
            return False

    # Must have some actual reason text
    if len(reason.strip()) < 3:
        print(f"[validate_reason] Reason '{reason}' is INVALID (too short)")
        return False

    print(f"[validate_reason] Reason '{reason}' is valid")
    return True


def start_reason_validation(state: dict) -> dict:
    """
    Start async reason validation - simulates calling an external validation service.

    This function initiates an async operation and returns a "pending" status.
    The workflow will interrupt and wait for the external service to call back
    with the result.

    In production, this would:
    1. Call an external fraud detection API
    2. Register a webhook callback
    3. Return pending with job_id

    Args:
        state: Workflow state containing return_reason

    Returns:
        dict with status="pending" and metadata, OR the actual result if sync
    """
    import uuid

    reason = state.get('return_reason', '')
    order_id = state.get('order_id', '')

    # Generate a job ID for tracking
    job_id = f"val_{uuid.uuid4().hex[:8]}"

    print("=" * 50)
    print("[start_reason_validation] Starting async validation")
    print(f"  Job ID: {job_id}")
    print(f"  Order: {order_id}")
    print(f"  Reason: {reason}")
    print("  Status: PENDING - Waiting for external validation service")
    print("=" * 50)

    # Return pending to trigger async interrupt
    # The workflow will pause here until resume is called with the result
    return {
        "status": "pending",
        "job_id": job_id,
        "order_id": order_id,
        "reason": reason,
        "message": "Validating return reason with external service..."
    }


def process_return(state: dict) -> bool:
    """
    Process the return request.

    In production, this would:
    1. Create return record in database
    2. Generate return shipping label
    3. Send confirmation email
    4. Update order status
    5. Reserve refund amount

    Args:
        state: Workflow state with order_id and return_reason

    Returns:
        True if processing succeeded
    """
    order_id = state.get('order_id')
    reason = state.get('return_reason')

    print("=" * 50)
    print("[process_return] Processing return request:")
    print(f"  Order ID: {order_id}")
    print(f"  Reason: {reason}")
    print("  Status: APPROVED")
    print("  Action: Return label will be sent via email")
    print("=" * 50)

    return True
