from primfunctions.utils.streaming import (
    update_sentence_buffer,
    PUNCTUATION_BY_LANGUAGE,
)


def run_test(test_name, test_func):
    """Helper to run a single test and print results"""
    try:
        test_func()
        print(f"✓ {test_name}")
        return True
    except AssertionError as e:
        print(f"✗ {test_name}")
        print(f"  Error: {e}")
        return False
    except Exception as e:
        print(f"✗ {test_name}")
        print(f"  Unexpected error: {e}")
        return False


def test_dollar_amount_whole():
    """Test dollar amount with whole number like $20."""
    buffer = ""
    buffer, sentence = update_sentence_buffer("The total is $20. Ready to", buffer)
    assert sentence == "The total is $20."
    assert buffer == " Ready to"


def test_dollar_amount_decimal():
    """Test dollar amount with decimal like $20.99."""
    buffer = ""
    buffer, sentence = update_sentence_buffer("The price is $20.99.", buffer)
    assert sentence == "The price is $20.99."
    assert buffer == ""


def test_dollar_amount_small_decimal():
    """Test dollar amount with small decimal like $2.35."""
    buffer = ""
    buffer, sentence = update_sentence_buffer("It costs $2.35.", buffer)
    assert sentence == "It costs $2.35."
    assert buffer == ""


def test_dollar_amount_streaming():
    """Test streaming dollar amount progressively"""
    buffer = ""

    # Stream "$20."
    buffer, sentence = update_sentence_buffer("The cost is $20.", buffer)
    assert sentence is None, f"Expected None but got '{sentence}', buffer='{buffer}'"
    assert buffer == "The cost is $20.", f"Expected 'The cost is $20.' but got '{buffer}'"

    # Test with decimal streaming
    buffer = ""
    buffer, sentence = update_sentence_buffer("Price: $", buffer)
    assert sentence is None, f"Expected None but got '{sentence}', buffer='{buffer}'"

    buffer, sentence = update_sentence_buffer("20.", buffer)
    assert sentence is None, f"Expected None but got '{sentence}', buffer='{buffer}'"

    buffer, sentence = update_sentence_buffer("99", buffer)
    assert sentence is None, f"Expected None but got '{sentence}', buffer='{buffer}'"

    buffer, sentence = update_sentence_buffer(".", buffer)
    assert sentence == "Price: $20.99.", f"Expected 'Price: $20.99.' but got '{sentence}', buffer='{buffer}'"
    assert buffer == "", f"Expected empty buffer but got '{buffer}'"

    # Test with decimal streaming
    buffer = ""
    buffer, sentence = update_sentence_buffer("Price: $", buffer)
    assert sentence is None, f"Expected None but got '{sentence}', buffer='{buffer}'"

    buffer, sentence = update_sentence_buffer("20", buffer)
    assert sentence is None, f"Expected None but got '{sentence}', buffer='{buffer}'"

    buffer, sentence = update_sentence_buffer(".99", buffer)
    assert sentence is None, f"Expected None but got '{sentence}', buffer='{buffer}'"

    buffer, sentence = update_sentence_buffer(".", buffer)
    assert sentence == "Price: $20.99.", f"Expected 'Price: $20.99.' but got '{sentence}', buffer='{buffer}'"
    assert buffer == "", f"Expected empty buffer but got '{buffer}'"

    # Test with comma-formatted dollar amount streaming (e.g., $4,000.00)
    buffer = ""
    buffer, sentence = update_sentence_buffer("Bitcoin reached $", buffer)
    assert sentence is None, f"Expected None but got '{sentence}', buffer='{buffer}'"

    buffer, sentence = update_sentence_buffer("4", buffer)
    assert sentence is None, f"Expected None but got '{sentence}', buffer='{buffer}'"

    buffer, sentence = update_sentence_buffer(",", buffer)
    assert sentence is None, f"Expected None but got '{sentence}', buffer='{buffer}'"

    buffer, sentence = update_sentence_buffer("000", buffer)
    assert sentence is None, f"Expected None but got '{sentence}', buffer='{buffer}'"

    buffer, sentence = update_sentence_buffer(".", buffer)
    assert sentence is None, f"Expected None but got '{sentence}', buffer='{buffer}'"

    buffer, sentence = update_sentence_buffer("00", buffer)
    assert sentence is None, f"Expected None but got '{sentence}', buffer='{buffer}'"

    buffer, sentence = update_sentence_buffer(".", buffer)
    assert sentence == "Bitcoin reached $4,000.00.", f"Expected 'Bitcoin reached $4,000.00.' but got '{sentence}', buffer='{buffer}'"
    assert buffer == "", f"Expected empty buffer but got '{buffer}'"


if __name__ == "__main__":
    print("Running update_sentence_buffer tests...\n")

    # List of all test functions
    tests = [
        ("Dollar amount whole number ($20.)", test_dollar_amount_whole),
        ("Dollar amount with decimal ($20.99.)", test_dollar_amount_decimal),
        ("Dollar amount small decimal ($2.35.)", test_dollar_amount_small_decimal),
        ("Dollar amount streaming", test_dollar_amount_streaming),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        if run_test(test_name, test_func):
            passed += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"Tests completed: {passed} passed, {failed} failed")
    print(f"{'='*60}")
