import pytest

from words_segmentation.tokenizer import WordsSegmentationTokenizer


def test_tokenizer_with_max_characters():
    """Test WordsSegmentationTokenizer with max_characters parameter."""
    tokenizer = WordsSegmentationTokenizer(max_characters=5)
    text = "hello world testing"
    tokens = tokenizer.tokenize(text)

    assert "".join(tokens) == text
    assert all(len(token) <= 5 for token in tokens)
    assert tokens == ["hello", " ", "world", " ", "testi", "ng"]


def test_tokenizer_with_max_bytes():
    """Test WordsSegmentationTokenizer with max_bytes parameter."""
    tokenizer = WordsSegmentationTokenizer(max_bytes=8)
    text = "hello world testing"
    tokens = tokenizer.tokenize(text)

    assert "".join(tokens) == text
    assert all(len(token.encode('utf-8')) <= 8 for token in tokens)


def test_tokenizer_characters_hebrew():
    """Test tokenizer with Hebrew text using max_characters."""
    tokenizer = WordsSegmentationTokenizer(max_characters=4)
    text = "עמית מוריוסף"
    tokens = tokenizer.tokenize(text)

    assert "".join(tokens) == text
    assert all(len(token) <= 4 for token in tokens)
    assert tokens == ['עמית', ' ', 'מורי', 'וסף']


def test_tokenizer_characters_emoji():
    """Test tokenizer with emoji using max_characters."""
    tokenizer = WordsSegmentationTokenizer(max_characters=8)
    text = "hello 😀 world 🌟"
    tokens = tokenizer.tokenize(text)

    assert "".join(tokens) == text
    assert all(len(token) <= 8 for token in tokens)


def test_tokenizer_no_limit():
    """Test tokenizer without character or byte limits."""
    tokenizer = WordsSegmentationTokenizer()
    text = "hello world testing"
    tokens = tokenizer.tokenize(text)

    assert "".join(tokens) == text
    # Without limits, words should not be split (but have trailing spaces)
    assert tokens == ["hello ", "world ", "testing"]


def test_tokenizer_characters_vs_bytes_hebrew():
    """Test difference between character and byte limits with Hebrew."""
    text = "עמית מוריוסף"

    # Hebrew characters are 2 bytes each in UTF-8
    tokenizer_chars = WordsSegmentationTokenizer(max_characters=4)
    tokens_chars = tokenizer_chars.tokenize(text)

    tokenizer_bytes = WordsSegmentationTokenizer(max_bytes=6)
    tokens_bytes = tokenizer_bytes.tokenize(text)

    # Both should reconstruct the original text
    assert "".join(tokens_chars) == text
    assert "".join(tokens_bytes) == text

    # Character-based splitting produces different result than byte-based
    assert tokens_chars == ['עמית', ' ', 'מורי', 'וסף']
    assert tokens_bytes == ['עמי', 'ת ', 'מור', 'יוס', 'ף']

    # Verify constraints
    assert all(len(token) <= 4 for token in tokens_chars)
    assert all(len(token.encode('utf-8')) <= 6 for token in tokens_bytes)


def test_tokenizer_characters_json():
    """Test tokenizer with JSON using max_characters."""
    tokenizer = WordsSegmentationTokenizer(max_characters=10)
    json_text = '{"name": "test", "value": 123}'
    tokens = tokenizer.tokenize(json_text)

    assert "".join(tokens) == json_text
    assert all(len(token) <= 10 for token in tokens)


def test_tokenizer_characters_empty_string():
    """Test tokenizer with empty string."""
    tokenizer = WordsSegmentationTokenizer(max_characters=10)
    tokens = tokenizer.tokenize("")

    assert tokens == []


def test_tokenizer_characters_multiline():
    """Test tokenizer with multiline text using max_characters."""
    tokenizer = WordsSegmentationTokenizer(max_characters=10)
    text = """
    def foo():
        return "bar"
    """.strip()
    tokens = tokenizer.tokenize(text)

    assert "".join(tokens) == text
    assert all(len(token) <= 10 for token in tokens)


def test_tokenizer_complex_emoji_characters():
    """Test tokenizer with complex emoji cluster using max_characters."""
    tokenizer = WordsSegmentationTokenizer(max_characters=5)
    # Note: This emoji cluster is counted as 7 characters by Python's len()
    # (individual code points), not as 1 grapheme cluster
    text = "hi 👩‍👩‍👧‍👦 bye"
    tokens = tokenizer.tokenize(text)

    assert "".join(tokens) == text
    # The emoji gets split because Python counts code points, not graphemes
    # Just verify the text reconstructs correctly
    assert all(len(token) <= 5 for token in tokens)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
