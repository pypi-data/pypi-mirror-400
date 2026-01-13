import pytest
from respparser.parser import RespParser


@pytest.fixture
def parser():
    return RespParser()


def test_parse_valid_array(parser):
    """Test parsing a valid RESP array like *3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n."""
    data = b"*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n"
    assert parser.parse(data) == [b"SET", b"foo", b"bar"]


def test_parse_empty_input(parser):
    """Test parsing empty bytes."""
    assert parser.parse(b"") == []


def test_parse_null_bulk_string(parser):
    """Test parsing an array with a null bulk string."""
    data = b"*2\r\n$3\r\nGET\r\n$-1\r\n"
    assert parser.parse(data) == [b"GET", None]


def test_parse_invalid_header(parser):
    """Test parsing an invalid array header (not starting with *)."""
    data = b"$3\r\nSET\r\n"
    with pytest.raises(
        ValueError, match="Expected a RESP array starting with \\*, but got: b'\\$3'"
    ):
        parser.parse(data)


def test_parse_non_numeric_header(parser):
    """Test parsing an array header with non-numeric value."""
    data = b"*abc\r\n$3\r\nSET\r\n"
    with pytest.raises(
        ValueError,
        match="Expected a number after \\* \\(like \\*3\\), but got: b'\\*abc'",
    ):
        parser.parse(data)


def test_parse_incomplete_array(parser):
    """Test parsing an array with fewer lines than expected."""
    data = b"*3\r\n$3\r\nSET\r\n$3\r\n"
    with pytest.raises(ValueError, match="Missing the data after the length line"):
        parser.parse(data)


def test_parse_ran_out_of_lines(parser):
    """Test parsing an array with fewer lines than expected."""
    data = b"*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n"
    with pytest.raises(
        ValueError, match="Ran out of lines before finishing the command"
    ):
        parser.parse(data)


def test_parse_invalid_bulk_string_length(parser):
    """Test parsing a bulk string with invalid length."""
    data = b"*2\r\n$abc\r\nSET\r\n"
    with pytest.raises(
        ValueError,
        match="Expected a number after \\$ \\(like \\$3\\), but got: b'\\$abc'",
    ):
        parser.parse(data)


def test_parse_length_mismatch(parser):
    """Test parsing a bulk string with data length not matching $n."""
    data = b"*2\r\n$3\r\nSE\r\n$3\r\nfoo\r\n"
    with pytest.raises(ValueError, match="Expected 3 bytes, but got 2 in: b'SE'"):
        parser.parse(data)


def test_parse_missing_data_line(parser):
    """Test parsing an array missing the data line after $n."""
    data = b"*2\r\n$3\r\nSET\r\n$3\r\n"
    with pytest.raises(ValueError, match="Missing the data after the length line"):
        parser.parse(data)
