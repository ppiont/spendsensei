"""Test script for guardrails functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spendsense.utils.guardrails import check_tone, check_consent, DISCLAIMER


def test_check_tone():
    """Test tone checking with various inputs."""
    print("=" * 60)
    print("Testing check_tone() function")
    print("=" * 60)

    # Test cases: (text, should_pass)
    test_cases = [
        # Should pass (neutral language)
        ("You have high spending patterns in certain categories", True),
        ("Your credit utilization is currently at 77%", True),
        ("Consider reviewing your subscription services", True),
        ("You may benefit from building an emergency fund", True),
        ("Your income shows some variability", True),

        # Should fail (shaming language)
        ("You're overspending on unnecessary items", False),
        ("This shows bad financial habits", False),
        ("You've been irresponsible with your credit cards", False),
        ("Stop being careless with your money", False),
        ("You're wasting money on subscriptions", False),
        ("These poor choices are hurting your finances", False),

        # Edge cases
        ("", True),  # Empty string should pass
        ("YOU'RE OVERSPENDING", False),  # Case insensitive
    ]

    passed = 0
    failed = 0

    for text, should_pass in test_cases:
        is_valid, violations = check_tone(text)

        # Check if result matches expectation
        test_passed = (is_valid == should_pass)

        if test_passed:
            passed += 1
            status = "✓ PASS"
        else:
            failed += 1
            status = "✗ FAIL"

        # Print result
        print(f"\n{status}")
        print(f"  Text: {text[:50]}...")
        print(f"  Expected: {'Pass' if should_pass else 'Fail'}")
        print(f"  Got: {'Pass' if is_valid else 'Fail'}")
        if violations:
            print(f"  Violations: {violations}")

    print(f"\n{'=' * 60}")
    print(f"check_tone() Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}\n")

    return failed == 0


def test_check_consent():
    """Test consent checking."""
    print("=" * 60)
    print("Testing check_consent() function")
    print("=" * 60)

    # Test cases: (consent_value, expected_result)
    test_cases = [
        (True, True),
        (False, False),
        (None, False),
    ]

    passed = 0
    failed = 0

    for consent_value, expected in test_cases:
        result = check_consent(consent_value)

        test_passed = (result == expected)

        if test_passed:
            passed += 1
            status = "✓ PASS"
        else:
            failed += 1
            status = "✗ FAIL"

        print(f"\n{status}")
        print(f"  Input: {consent_value}")
        print(f"  Expected: {expected}")
        print(f"  Got: {result}")

    print(f"\n{'=' * 60}")
    print(f"check_consent() Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}\n")

    return failed == 0


def test_disclaimer():
    """Test disclaimer constant."""
    print("=" * 60)
    print("Testing DISCLAIMER constant")
    print("=" * 60)

    print(f"\nDisclaimer text:\n{DISCLAIMER}")

    # Check that disclaimer has expected keywords
    required_keywords = ["educational", "financial advice", "professional"]

    passed = 0
    failed = 0

    for keyword in required_keywords:
        if keyword.lower() in DISCLAIMER.lower():
            print(f"✓ Contains '{keyword}'")
            passed += 1
        else:
            print(f"✗ Missing '{keyword}'")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"DISCLAIMER Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}\n")

    return failed == 0


def main():
    """Run all guardrails tests."""
    print("\n" + "=" * 60)
    print("GUARDRAILS TEST SUITE")
    print("=" * 60 + "\n")

    results = []

    # Run all tests
    results.append(("check_tone", test_check_tone()))
    results.append(("check_consent", test_check_consent()))
    results.append(("DISCLAIMER", test_disclaimer()))

    # Summary
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
