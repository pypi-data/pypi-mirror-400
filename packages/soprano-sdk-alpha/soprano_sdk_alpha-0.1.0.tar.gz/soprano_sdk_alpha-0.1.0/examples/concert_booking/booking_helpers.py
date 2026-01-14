"""
Helper functions for concert ticket booking workflow
"""
import random
import uuid


def initialize_prices(state):
    """Initialize ticket prices"""
    return {
        'vip_price': 5000,
        'premium_price': 3000,
        'general_price': 1500
    }


def check_availability(state):
    """Check if requested seats are available"""
    seat_preference = state.get('seat_preference')
    ticket_quantity = state.get('ticket_quantity', 1)

    # Simulate availability check - 80% chance of success
    available = random.random() > 0.2

    print(f"Checking availability: {ticket_quantity} x {seat_preference} seats")
    print(f"Result: {'Available' if available else 'Not Available'}")

    return available


def process_payment(state):
    """Process payment for tickets"""
    customer_name = state.get('customer_name')
    concert_name = state.get('concert_name')
    seat_preference = state.get('seat_preference')
    ticket_quantity = state.get('ticket_quantity', 1)

    # Calculate total amount
    vip_price = state.get('vip_price', 5000)
    premium_price = state.get('premium_price', 3000)
    general_price = state.get('general_price', 1500)

    prices = {
        'VIP': vip_price,
        'Premium': premium_price,
        'General': general_price
    }

    price_per_ticket = prices.get(seat_preference, general_price)
    total_amount = price_per_ticket * ticket_quantity

    # Simulate payment processing - 90% success rate
    payment_success = random.random() > 0.1

    print(f"Processing payment for {customer_name}")
    print(f"Concert: {concert_name}")
    print(f"Tickets: {ticket_quantity} x {seat_preference}")
    print(f"Total: ₹{total_amount}")
    print(f"Payment Status: {'Success' if payment_success else 'Failed'}")

    # Generate booking reference on success
    if payment_success:
        state['booking_reference'] = f"BK{uuid.uuid4().hex[:8].upper()}"

    return payment_success


def send_confirmation(state):
    """Send booking confirmation"""
    customer_name = state.get('customer_name')
    booking_reference = state.get('booking_reference')
    concert_name = state.get('concert_name')

    # Simulate sending confirmation - 95% success rate
    confirmation_sent = random.random() > 0.05

    print(f"Sending confirmation to {customer_name}")
    print(f"Booking Reference: {booking_reference}")
    print(f"Concert: {concert_name}")
    print(f"Status: {'Sent' if confirmation_sent else 'Failed'}")

    return confirmation_sent


def handle_payment_failure(state):
    """Handle payment failure"""
    print("Payment failed. Cleaning up...")
    return False
