"""
Business logic functions for profile inquiry workflow.

Each function receives the full workflow state dict and returns a result.
These are mock implementations for demonstration purposes.
"""

from datetime import datetime, timedelta
import hashlib


def lookup_profile(state: dict) -> dict:
    """
    Look up customer profile by identifier (email, phone, or customer ID).

    In production, this would:
    - Query customer database
    - Retrieve account details
    - Get loyalty program status

    Args:
        state: Workflow state containing customer_identifier

    Returns:
        dict with "found" key for routing, plus profile details
    """
    identifier = state.get("customer_identifier", "").lower().strip()

    # Mock logic: identifiers containing "invalid" or "notfound" return not found
    if not identifier:
        print("[lookup_profile] No identifier provided")
        return {"found": False}

    if "invalid" in identifier or "notfound" in identifier or "unknown" in identifier:
        print(f"[lookup_profile] Profile NOT FOUND for: {identifier}")
        return {"found": False}

    # Generate deterministic mock data based on identifier
    # This ensures same identifier always returns same profile
    hash_val = int(hashlib.md5(identifier.encode()).hexdigest()[:8], 16)

    # Generate mock profile
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia"]
    states = ["NY", "CA", "IL", "TX", "AZ", "PA"]

    first_name = first_names[hash_val % len(first_names)]
    last_name = last_names[(hash_val >> 4) % len(last_names)]
    tier = tiers[(hash_val >> 8) % len(tiers)]
    city = cities[(hash_val >> 12) % len(cities)]
    state_abbr = states[(hash_val >> 12) % len(states)]

    # Generate email if not provided as identifier
    if "@" in identifier:
        email = identifier
    else:
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"

    # Generate phone if not provided as identifier
    if identifier.replace("-", "").replace("+", "").replace(" ", "").isdigit():
        phone = identifier
    else:
        phone = f"+1-555-{str(hash_val)[-4:]}"

    # Generate customer ID
    customer_id = f"CUST-{str(hash_val)[-6:].upper()}"

    # Calculate member since date (1-5 years ago)
    years_ago = (hash_val % 5) + 1
    member_since = (datetime.now() - timedelta(days=365 * years_ago)).strftime("%Y-%m-%d")

    # Calculate loyalty points
    loyalty_points = (hash_val % 10000) + 500

    profile = {
        "found": True,
        "customer_id": customer_id,
        "name": f"{first_name} {last_name}",
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "address": f"{100 + (hash_val % 900)} Main St",
        "city": city,
        "state": state_abbr,
        "zip_code": f"{10000 + (hash_val % 90000)}",
        "member_since": member_since,
        "loyalty_tier": tier,
        "loyalty_points": loyalty_points,
    }

    print(f"[lookup_profile] Profile FOUND for: {identifier}")
    print(f"  Customer: {profile['name']} ({profile['customer_id']})")
    print(f"  Tier: {profile['loyalty_tier']} - {profile['loyalty_points']} points")

    return profile
