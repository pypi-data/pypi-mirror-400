import pytest
from respparser.parser import RespSerializer


@pytest.fixture
def serializer():
    return RespSerializer()


def test_serialize_simple_string(serializer):
    """Test serializing a simple string."""
    assert serializer.serialize("+OK") == b"+OK\r\n"


def test_serialize_error(serializer):
    """Test serializing an error."""
    assert serializer.serialize("-ERR") == b"-ERR\r\n"


def test_serialize_null(serializer):
    """Test serializing None (null bulk string)."""
    assert serializer.serialize(None) == b"$-1\r\n"


def test_serialize_bulk_string(serializer):
    """Test serializing a bulk string."""
    assert serializer.serialize("foo") == b"$3\r\nfoo\r\n"


def test_serialize_integer(serializer):
    """Test serializing an integer."""
    assert serializer.serialize(42) == b":42\r\n"


def test_serialize_unsupported_type(serializer):
    """Test serializing an unsupported type."""
    with pytest.raises(
        ValueError, match="Unsupported data type for serialization: <class 'list'>"
    ):
        serializer.serialize([1, 2, 3])
