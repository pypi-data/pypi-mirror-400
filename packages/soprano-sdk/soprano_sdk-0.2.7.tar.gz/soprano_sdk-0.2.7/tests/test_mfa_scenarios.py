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


def test_mfa_default_max_attempts():
    """
    Test Case 8: Verify default max_attempts value

    Validates that:
    - MFA collector nodes use default max_attempts value of 3 when not specified
    """
    print("\n" + "=" * 80)
    print("TEST 8: MFA Default Max Attempts")
    print("=" * 80)

    yaml_path = os.path.join(get_examples_dir(), "concert_ticket_booking.yaml")
    graph, engine = load_workflow(yaml_path)

    print("\nScenario: MFA config does not specify max_attempts")
    print("Expected: Default value of 3 should be used")

    # Get MFA validate nodes
    mfa_validate_nodes = [s for s in engine.list_steps() if '_mfa_validate' in s]
    print(f"\nMFA validate nodes: {mfa_validate_nodes}")

    for node_id in mfa_validate_nodes:
        node_info = engine.get_step_info(node_id)
        max_attempts = node_info.get('max_attempts', 'NOT_SET')
        print(f"\n{node_id}")
        print(f"  max_attempts: {max_attempts}")

        assert max_attempts == 3, \
            f"Expected default max_attempts=3, got {max_attempts}"
        print("  ✅ Correctly uses default max_attempts=3")

    print("\n✅ TEST PASSED: Default max_attempts value verified")
    print("=" * 80)


def test_mfa_custom_max_attempts():
    """
    Test Case 9: Verify custom max_attempts configuration

    Validates that:
    - Custom max_attempts value from MFA config is applied to collector node
    """
    print("\n" + "=" * 80)
    print("TEST 9: MFA Custom Max Attempts")
    print("=" * 80)

    # Create a temporary YAML with custom max_attempts
    import tempfile

    yaml_path = os.path.join(get_examples_dir(), "concert_ticket_booking.yaml")

    with open(yaml_path, 'r') as f:
        yaml_content = f.read()

    # Add max_attempts to first MFA config
    modified_yaml = yaml_content.replace(
        """    mfa:
      model: gpt-4o-mini
      type: REST
      payload:
        transactionType: CONCERT_TICKET_PAYMENT""",
        """    mfa:
      model: gpt-4o-mini
      type: REST
      max_attempts: 5
      payload:
        transactionType: CONCERT_TICKET_PAYMENT"""
    )

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_yaml_path = f.name
        f.write(modified_yaml)

    try:
        graph, engine = load_workflow(temp_yaml_path)

        print("\nScenario: MFA config specifies max_attempts: 5")

        # Find the process_payment MFA validate node
        process_payment_validate = 'process_payment_mfa_validate'
        assert process_payment_validate in engine.list_steps(), \
            f"Expected {process_payment_validate} node to exist"

        node_info = engine.get_step_info(process_payment_validate)
        max_attempts = node_info.get('max_attempts')

        print(f"\nNode: {process_payment_validate}")
        print(f"  max_attempts: {max_attempts}")

        assert max_attempts == 5, \
            f"Expected custom max_attempts=5, got {max_attempts}"
        print("  ✅ Correctly uses custom max_attempts=5")

        print("\n✅ TEST PASSED: Custom max_attempts value applied correctly")
        print("=" * 80)
    finally:
        # Clean up temporary file
        os.unlink(temp_yaml_path)


def test_mfa_custom_error_message():
    """
    Test Case 10: Verify custom on_max_attempts_reached message

    Validates that:
    - Custom error message from MFA config is applied to collector node
    """
    print("\n" + "=" * 80)
    print("TEST 10: MFA Custom Error Message")
    print("=" * 80)

    # Create a temporary YAML with custom error message
    import tempfile

    yaml_path = os.path.join(get_examples_dir(), "concert_ticket_booking.yaml")

    with open(yaml_path, 'r') as f:
        yaml_content = f.read()

    custom_error = "You have exceeded the maximum MFA attempts for payment verification. Your transaction has been blocked for security. Please contact support at 1-800-TICKETS."

    # Add on_max_attempts_reached to first MFA config
    modified_yaml = yaml_content.replace(
        """    mfa:
      model: gpt-4o-mini
      type: REST
      payload:
        transactionType: CONCERT_TICKET_PAYMENT""",
        f"""    mfa:
      model: gpt-4o-mini
      type: REST
      on_max_attempts_reached: "{custom_error}"
      payload:
        transactionType: CONCERT_TICKET_PAYMENT"""
    )

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_yaml_path = f.name
        f.write(modified_yaml)

    try:
        graph, engine = load_workflow(temp_yaml_path)

        print("\nScenario: MFA config specifies custom on_max_attempts_reached message")

        # Find the process_payment MFA validate node
        process_payment_validate = 'process_payment_mfa_validate'
        assert process_payment_validate in engine.list_steps(), \
            f"Expected {process_payment_validate} node to exist"

        node_info = engine.get_step_info(process_payment_validate)
        error_message = node_info.get('on_max_attempts_reached')

        print(f"\nNode: {process_payment_validate}")
        print(f"  on_max_attempts_reached: {error_message}")

        assert error_message == custom_error, \
            f"Expected custom error message, got {error_message}"
        print("  ✅ Correctly uses custom error message")

        print("\n✅ TEST PASSED: Custom error message applied correctly")
        print("=" * 80)
    finally:
        # Clean up temporary file
        os.unlink(temp_yaml_path)


def test_mfa_custom_max_attempts_and_error():
    """
    Test Case 11: Verify both custom max_attempts and on_max_attempts_reached together

    Validates that:
    - Both custom max_attempts and error message can be configured together
    - Both values are correctly applied to the MFA collector node
    """
    print("\n" + "=" * 80)
    print("TEST 11: MFA Custom Max Attempts and Error Message Together")
    print("=" * 80)

    # Create a temporary YAML with both custom values
    import tempfile

    yaml_path = os.path.join(get_examples_dir(), "concert_ticket_booking.yaml")

    with open(yaml_path, 'r') as f:
        yaml_content = f.read()

    custom_error = "Maximum verification attempts exceeded. Account locked."
    custom_max_attempts = 2

    # Add both fields to MFA config
    modified_yaml = yaml_content.replace(
        """    mfa:
      model: gpt-4o-mini
      type: REST
      payload:
        transactionType: CONCERT_TICKET_PAYMENT""",
        f"""    mfa:
      model: gpt-4o-mini
      type: REST
      max_attempts: {custom_max_attempts}
      on_max_attempts_reached: "{custom_error}"
      payload:
        transactionType: CONCERT_TICKET_PAYMENT"""
    )

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_yaml_path = f.name
        f.write(modified_yaml)

    try:
        graph, engine = load_workflow(temp_yaml_path)

        print(f"\nScenario: MFA config specifies max_attempts: {custom_max_attempts} and custom error")

        # Find the process_payment MFA validate node
        process_payment_validate = 'process_payment_mfa_validate'
        assert process_payment_validate in engine.list_steps(), \
            f"Expected {process_payment_validate} node to exist"

        node_info = engine.get_step_info(process_payment_validate)
        max_attempts = node_info.get('max_attempts')
        error_message = node_info.get('on_max_attempts_reached')

        print(f"\nNode: {process_payment_validate}")
        print(f"  max_attempts: {max_attempts}")
        print(f"  on_max_attempts_reached: {error_message}")

        assert max_attempts == custom_max_attempts, \
            f"Expected max_attempts={custom_max_attempts}, got {max_attempts}"
        print(f"  ✅ Correctly uses custom max_attempts={custom_max_attempts}")

        assert error_message == custom_error, \
            f"Expected custom error message, got {error_message}"
        print("  ✅ Correctly uses custom error message")

        print("\n✅ TEST PASSED: Both custom values applied correctly")
        print("=" * 80)
    finally:
        # Clean up temporary file
        os.unlink(temp_yaml_path)


def test_mfa_custom_headers_with_jinja():
    """
    Test Case 12: Verify custom headers with Jinja template rendering

    Validates that:
    - Custom headers can be specified in MFA config
    - Jinja templates in header values are correctly rendered with state data
    - Headers are stored in the MFA state as post_headers
    """
    print("\n" + "=" * 80)
    print("TEST 12: MFA Custom Headers with Jinja Template Rendering")
    print("=" * 80)

    # Create a temporary YAML with custom headers
    import tempfile

    yaml_path = os.path.join(get_examples_dir(), "concert_ticket_booking.yaml")

    with open(yaml_path, 'r') as f:
        yaml_content = f.read()

    # Add headers to first MFA config
    modified_yaml = yaml_content.replace(
        """    mfa:
      model: gpt-4o-mini
      type: REST
      payload:
        transactionType: CONCERT_TICKET_PAYMENT
        businessKey:
          customerName: "{{customer_name}}"
          concertName: "{{concert_name}}"
          seatPreference: "{{seat_preference}}"
          ticketQuantity: "{{ticket_quantity}}"
    transitions:""",
        """    mfa:
      model: gpt-4o-mini
      type: REST
      payload:
        transactionType: CONCERT_TICKET_PAYMENT
        businessKey:
          customerName: "{{customer_name}}"
          concertName: "{{concert_name}}"
          seatPreference: "{{seat_preference}}"
          ticketQuantity: "{{ticket_quantity}}"
      headers:
        Authorization: "Bearer {{bearer_token}}"
        X-Customer-Name: "{{customer_name}}"
        X-Concert-Name: "{{concert_name}}"
        X-Request-Id: "payment-{{booking_reference}}"
    transitions:"""
    )

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_yaml_path = f.name
        f.write(modified_yaml)

    try:
        graph, engine = load_workflow(temp_yaml_path)

        print("\nScenario: MFA config includes custom headers with Jinja templates")

        # Initialize state with test data
        state = {
            'bearer_token': 'test-token-12345',
            'customer_name': 'John Doe',
            'concert_name': 'Rock Concert 2026',
            'booking_reference': 'BK-001',
            'seat_preference': 'VIP',
            'ticket_quantity': 2
        }

        # Find the process_payment step
        process_payment_step = 'process_payment'
        assert process_payment_step in engine.list_steps(), \
            f"Expected {process_payment_step} step to exist"

        # Check the MFA start node - this is where the MFA config is stored
        process_payment_mfa_start = 'process_payment_mfa_start'
        assert process_payment_mfa_start in engine.list_steps(), \
            f"Expected {process_payment_mfa_start} node to exist"

        mfa_start_info = engine.get_step_info(process_payment_mfa_start)

        # Verify headers are defined in MFA config
        assert 'mfa' in mfa_start_info, "MFA start node should have MFA configuration"
        assert 'headers' in mfa_start_info['mfa'], "MFA config should have headers"

        headers_config = mfa_start_info['mfa']['headers']
        print("\nHeaders defined in MFA config:")
        for key, value in headers_config.items():
            print(f"  {key}: {value}")

        # Verify header templates
        assert headers_config['Authorization'] == "Bearer {{bearer_token}}", \
            "Authorization header should have bearer_token template"
        assert headers_config['X-Customer-Name'] == "{{customer_name}}", \
            "X-Customer-Name header should have customer_name template"
        assert headers_config['X-Concert-Name'] == "{{concert_name}}", \
            "X-Concert-Name header should have concert_name template"
        assert headers_config['X-Request-Id'] == "payment-{{booking_reference}}", \
            "X-Request-Id header should have booking_reference template"

        print("\n✅ Headers configuration verified")

        # Test that headers would be rendered correctly (simulation)
        from jinja2 import Environment
        template_loader = Environment()

        expected_rendered_headers = {
            'Authorization': 'Bearer test-token-12345',
            'X-Customer-Name': 'John Doe',
            'X-Concert-Name': 'Rock Concert 2026',
            'X-Request-Id': 'payment-BK-001'
        }

        print("\nExpected rendered headers:")
        for key, value in expected_rendered_headers.items():
            print(f"  {key}: {value}")

        # Verify template rendering logic
        for key, template_str in headers_config.items():
            rendered = template_loader.from_string(template_str).render(state)
            expected = expected_rendered_headers[key]
            assert rendered == expected, \
                f"Header {key} rendering mismatch: expected '{expected}', got '{rendered}'"
            print(f"  ✅ {key} renders correctly")

        print("\n✅ TEST PASSED: Custom headers with Jinja templates work correctly")
        print("=" * 80)
    finally:
        # Clean up temporary file
        os.unlink(temp_yaml_path)
