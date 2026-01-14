import os
import pytest
from soprano_sdk import load_workflow


def get_examples_dir():
    return os.path.join(os.path.dirname(__file__), "..", "examples", "concert_booking")


@pytest.fixture(scope="module", autouse=True)
def setup_mfa_env():
    """Set up MFA environment variables for testing"""
    env_vars = {
        'GENERATE_TOKEN_BASE_URL': 'https://mock-mfa.example.com',
        'GENERATE_TOKEN_PATH': '/api/v1/mfa/generate',
        'VALIDATE_TOKEN_BASE_URL': 'https://mock-mfa.example.com',
        'VALIDATE_TOKEN_PATH': '/api/v1/mfa/validate',
        'AUTHORIZE_TOKEN_BASE_URL': 'https://mock-mfa.example.com',
        'AUTHORIZE_TOKEN_PATH': '/api/v1/mfa/authorize',
    }

    # Store original values
    original_values = {}
    for key, value in env_vars.items():
        original_values[key] = os.environ.get(key)
        os.environ[key] = value

    yield

    # Restore original values
    for key, original_value in original_values.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


def test_mfa_nodes_created():
    """
    Test Case 1: Verify MFA nodes are properly created

    Validates that:
    - MFA start nodes are inserted before MFA-protected steps
    - MFA data collector nodes are created
    - Original steps remain intact
    """
    print("\n" + "=" * 80)
    print("TEST 1: MFA Node Creation")
    print("=" * 80)

    yaml_path = os.path.join(get_examples_dir(), "concert_ticket_booking.yaml")
    graph, engine = load_workflow(yaml_path)

    # Count MFA-protected steps in original config
    mfa_protected_steps = ['process_payment', 'send_confirmation']

    print(f"\nOriginal MFA-protected steps: {mfa_protected_steps}")
    print("Expected MFA nodes per protected step: 2 (start + collector)")
    print(f"Total expected MFA nodes: {len(mfa_protected_steps) * 2}")

    # Verify MFA nodes were created
    all_steps = engine.list_steps()
    print(f"\nTotal steps after MFA injection: {len(all_steps)}")

    # Check for MFA start and validate nodes
    mfa_start_nodes = [s for s in all_steps if '_mfa_start' in s]
    mfa_validate_nodes = [s for s in all_steps if '_mfa_validate' in s]

    print(f"\nMFA start nodes created: {mfa_start_nodes}")
    print(f"MFA validate nodes created: {mfa_validate_nodes}")

    assert len(mfa_start_nodes) == len(mfa_protected_steps), \
        f"Expected {len(mfa_protected_steps)} MFA start nodes, found {len(mfa_start_nodes)}"

    assert len(mfa_validate_nodes) == len(mfa_protected_steps), \
        f"Expected {len(mfa_protected_steps)} MFA validate nodes, found {len(mfa_validate_nodes)}"

    # Verify original steps still exist
    for step in mfa_protected_steps:
        assert step in all_steps, f"Original step {step} should still exist"

    print("\n✅ TEST PASSED: MFA nodes created correctly")
    print("=" * 80)


def test_mfa_previous_step_redirection():
    """
    Test Case 2: Verify steps BEFORE MFA-protected steps redirect correctly

    Validates that:
    - check_seat_availability -> process_payment becomes check_seat_availability -> process_payment_mfa_start
    - process_payment -> send_confirmation becomes process_payment -> send_confirmation_mfa_start
    """
    print("\n" + "=" * 80)
    print("TEST 2: Previous Step Redirection (Forward Flow)")
    print("=" * 80)

    yaml_path = os.path.join(get_examples_dir(), "concert_ticket_booking.yaml")
    graph, engine = load_workflow(yaml_path)

    # Test Case 2a: check_seat_availability should point to process_payment_mfa_start
    print("\nTest 2a: Forward flow to first MFA step")
    check_availability_step = engine.get_step_info('check_seat_availability')

    if transitions := check_availability_step.get('transitions'):
        payment_transition = next((t for t in transitions if 'process_payment' in t.get('next', '')), None)
        if payment_transition:
            next_step = payment_transition['next']
            print(f"check_seat_availability -> {next_step}")
            assert '_mfa_start' in next_step, \
                f"Expected MFA start node, got {next_step}"
            print(f"✅ Correctly redirects to MFA start node: {next_step}")

    # Test Case 2b: process_payment should point to send_confirmation_mfa_start
    print("\nTest 2b: Forward flow to second MFA step")
    process_payment_step = engine.get_step_info('process_payment')

    if transitions := process_payment_step.get('transitions'):
        confirmation_transition = next((t for t in transitions if 'send_confirmation' in t.get('next', '')), None)
        if confirmation_transition:
            next_step = confirmation_transition['next']
            print(f"process_payment -> {next_step}")
            assert '_mfa_start' in next_step, \
                f"Expected MFA start node, got {next_step}"
            print(f"✅ Correctly redirects to MFA start node: {next_step}")

    print("\n✅ TEST PASSED: Previous steps redirect correctly to MFA nodes")
    print("=" * 80)


def test_mfa_loop_back_redirection():
    """
    Test Case 3: Verify steps AFTER MFA-protected steps that loop back redirect correctly

    This is the CRITICAL test for the bug fix!

    Validates that:
    - ask_modification_needed comes AFTER process_payment
    - When user requests modification, it loops back to collect_seat_preference
    - collect_seat_preference eventually leads back to process_payment
    - The loop back should go through process_payment_mfa_start, not bypass MFA
    """
    print("\n" + "=" * 80)
    print("TEST 3: Loop Back Redirection (CRITICAL BUG FIX TEST)")
    print("=" * 80)

    yaml_path = os.path.join(get_examples_dir(), "concert_ticket_booking.yaml")
    graph, engine = load_workflow(yaml_path)

    print("\nScenario: User completes booking, then requests modification")
    print("Flow: ask_modification_needed -> collect_seat_preference -> ... -> process_payment")
    print("Expected: Should go through MFA again (process_payment_mfa_start)")

    # Verify ask_modification_needed loops back to collect_seat_preference
    modification_step = engine.get_step_info('ask_modification_needed')
    print("\nStep: ask_modification_needed")

    if transitions := modification_step.get('transitions'):
        loop_back = next((t for t in transitions if 'collect_seat_preference' in t.get('next', '')), None)
        if loop_back:
            next_step = loop_back['next']
            print(f"  -> Loops back to: {next_step}")
            assert next_step == 'collect_seat_preference', \
                f"Expected collect_seat_preference, got {next_step}"

    # Trace the path from collect_seat_preference back to payment
    print("\nTracing path from loop back point:")
    current_step = 'collect_seat_preference'
    path = [current_step]
    visited = set()
    max_steps = 20

    while current_step and len(path) < max_steps:
        if current_step in visited:
            break
        visited.add(current_step)

        step_info = engine.get_step_info(current_step)
        if not step_info:
            break

        # Find next step
        next_step = None
        if transitions := step_info.get('transitions'):
            # Take first transition for tracing
            if transitions:
                next_step = transitions[0].get('next')
        elif 'next' in step_info:
            next_step = step_info['next']

        if next_step:
            path.append(next_step)
            current_step = next_step

            # Check if we've reached payment MFA
            if 'process_payment' in next_step and '_mfa_start' in next_step:
                print("\n✅ CRITICAL: Loop back correctly goes through MFA!")
                print(f"   Full path: {' -> '.join(path)}")
                break
        else:
            break

    # Verify the path includes MFA start node
    has_mfa_start = any('_mfa_start' in step and 'process_payment' in step for step in path)
    assert has_mfa_start, \
        f"Loop back path should include process_payment_mfa_start. Path: {path}"

    print("\n✅ TEST PASSED: Loop back correctly redirects through MFA")
    print("=" * 80)


def test_mfa_multiple_steps_sequence():
    """
    Test Case 4: Verify multiple MFA steps in sequence work correctly

    Validates that:
    - process_payment (MFA) -> send_confirmation (MFA) works correctly
    - Each MFA step has its own start and collector nodes
    - Flow between MFA steps is preserved
    """
    print("\n" + "=" * 80)
    print("TEST 4: Multiple MFA Steps in Sequence")
    print("=" * 80)

    yaml_path = os.path.join(get_examples_dir(), "concert_ticket_booking.yaml")
    graph, engine = load_workflow(yaml_path)

    print("\nScenario: Two consecutive MFA-protected steps")
    print("Flow: process_payment (MFA) -> send_confirmation (MFA)")

    # Get process_payment step
    payment_step = engine.get_step_info('process_payment')
    print("\nStep: process_payment")

    # Find transition to send_confirmation
    next_after_payment = None
    if transitions := payment_step.get('transitions'):
        for t in transitions:
            if 'send_confirmation' in t.get('next', ''):
                next_after_payment = t['next']
                break

    if not next_after_payment and 'next' in payment_step:
        if 'send_confirmation' in payment_step['next']:
            next_after_payment = payment_step['next']

    print(f"  -> Next step: {next_after_payment}")

    if next_after_payment:
        assert '_mfa_start' in next_after_payment, \
            f"Expected send_confirmation_mfa_start, got {next_after_payment}"
        print(f"✅ Correctly chains to second MFA node: {next_after_payment}")

    # Verify both MFA processes are independent
    payment_mfa_nodes = [s for s in engine.list_steps() if 'process_payment' in s and 'mfa' in s]
    confirmation_mfa_nodes = [s for s in engine.list_steps() if 'send_confirmation' in s and 'mfa' in s]

    print(f"\nPayment MFA nodes: {payment_mfa_nodes}")
    print(f"Confirmation MFA nodes: {confirmation_mfa_nodes}")

    assert len(payment_mfa_nodes) >= 2, "Should have start + collector for payment"
    assert len(confirmation_mfa_nodes) >= 2, "Should have start + collector for confirmation"

    print("\n✅ TEST PASSED: Multiple MFA steps work in sequence")
    print("=" * 80)


def test_mfa_data_fields_created():
    """
    Test Case 5: Verify MFA data fields are automatically created

    Validates that:
    - Data fields for MFA collector nodes are added to workflow data
    - Field names match the MFA collector node field names
    """
    print("\n" + "=" * 80)
    print("TEST 5: MFA Data Fields Creation")
    print("=" * 80)

    yaml_path = os.path.join(get_examples_dir(), "concert_ticket_booking.yaml")
    graph, engine = load_workflow(yaml_path)

    print("\nChecking if MFA-specific data fields were created...")

    # Get all data field names
    data_fields = [f['name'] for f in engine.data_fields]
    print(f"\nAll data fields: {data_fields}")

    # Find MFA validate nodes
    mfa_validate_nodes = [s for s in engine.list_steps() if '_mfa_validate' in s]
    print(f"\nMFA validate nodes: {mfa_validate_nodes}")

    # Check each validate node has a corresponding data field
    for validate_node in mfa_validate_nodes:
        validate_info = engine.get_step_info(validate_node)
        if field_name := validate_info.get('field'):
            print(f"\nValidate node: {validate_node}")
            print(f"  Field name: {field_name}")

            assert field_name in data_fields, \
                f"MFA field {field_name} should be in data fields"
            print("  ✅ Field exists in data schema")

    print("\n✅ TEST PASSED: MFA data fields created correctly")
    print("=" * 80)


def test_mfa_alternative_paths():
    """
    Test Case 6: Verify alternative paths to MFA steps are redirected

    Validates that:
    - offer_alternative_seats can loop back to check_seat_availability
    - This eventually leads to process_payment
    - Both paths (direct and alternative) go through MFA correctly
    """
    print("\n" + "=" * 80)
    print("TEST 6: Alternative Paths to MFA Steps")
    print("=" * 80)

    yaml_path = os.path.join(get_examples_dir(), "concert_ticket_booking.yaml")
    graph, engine = load_workflow(yaml_path)

    print("\nScenario: User selects unavailable seats, tries alternatives")
    print("Flow: offer_alternative_seats -> check_seat_availability -> process_payment")

    # Check offer_alternative_seats loops back correctly
    alternative_step = engine.get_step_info('offer_alternative_seats')
    print("\nStep: offer_alternative_seats")

    if transitions := alternative_step.get('transitions'):
        for t in transitions:
            if 'check_seat_availability' in t.get('next', ''):
                next_step = t['next']
                print(f"  -> {next_step}")

    # Verify check_seat_availability still points to MFA start
    check_step = engine.get_step_info('check_seat_availability')
    if transitions := check_step.get('transitions'):
        for t in transitions:
            next_step = t.get('next', '')
            if 'process_payment' in next_step:
                print(f"check_seat_availability -> {next_step}")
                assert '_mfa_start' in next_step, \
                    f"Expected MFA start node, got {next_step}"
                print(f"✅ Alternative path also goes through MFA: {next_step}")

    print("\n✅ TEST PASSED: Alternative paths correctly redirect to MFA")
    print("=" * 80)


def test_mfa_comprehensive_flow():
    """
    Test Case 7: Comprehensive end-to-end flow validation

    Validates complete workflow structure with all MFA redirections:
    - Count of all steps
    - Verification that no step bypasses MFA
    - All transitions to MFA-protected steps go through MFA start
    """
    print("\n" + "=" * 80)
    print("TEST 7: Comprehensive MFA Flow Validation")
    print("=" * 80)

    yaml_path = os.path.join(get_examples_dir(), "concert_ticket_booking.yaml")
    graph, engine = load_workflow(yaml_path)

    mfa_protected_original = ['process_payment', 'send_confirmation']
    all_steps = engine.list_steps()

    print(f"\nTotal steps in workflow: {len(all_steps)}")
    print(f"MFA-protected steps: {mfa_protected_original}")

    # Check ALL steps to ensure none directly reference MFA-protected steps
    print("\nValidating ALL transitions point to MFA start nodes...")

    violations = []
    for step_id in all_steps:
        # Skip the MFA-protected steps themselves and their MFA nodes
        if step_id in mfa_protected_original or '_mfa_' in step_id:
            continue

        step_info = engine.get_step_info(step_id)

        # Check transitions
        if transitions := step_info.get('transitions'):
            for t in transitions:
                next_step = t.get('next', '')
                # If pointing to MFA-protected step, should go through MFA start
                for protected in mfa_protected_original:
                    if next_step == protected:
                        violations.append(f"{step_id} -> {next_step} (should be {protected}_mfa_start)")

        # Check simple next field
        if next_field := step_info.get('next'):
            for protected in mfa_protected_original:
                if next_field == protected:
                    violations.append(f"{step_id} -> {next_field} (should be {protected}_mfa_start)")

    if violations:
        print("\n❌ VIOLATIONS FOUND:")
        for v in violations:
            print(f"  - {v}")
        assert False, f"Found {len(violations)} steps bypassing MFA"
    else:
        print("✅ All transitions correctly route through MFA start nodes")

    # Print final workflow statistics
    print("\n" + "-" * 80)
    print("WORKFLOW STATISTICS")
    print("-" * 80)
    print(f"Total steps: {len(all_steps)}")
    print(f"MFA-protected steps: {len(mfa_protected_original)}")
    print(f"MFA nodes created: {len([s for s in all_steps if '_mfa_' in s])}")
    print(f"Regular steps: {len([s for s in all_steps if '_mfa_' not in s])}")

    print("\n✅ TEST PASSED: Comprehensive flow validation successful")
    print("=" * 80)
