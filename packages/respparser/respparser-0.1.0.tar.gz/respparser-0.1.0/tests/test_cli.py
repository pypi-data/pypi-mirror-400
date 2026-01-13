import pytest
from click.testing import CliRunner
from respparser.cli import cli, decode_input


@pytest.fixture
def runner():
    return CliRunner()


def test_decode_input_valid():
    """Test decode_input with valid RESP string."""
    input_str = "*3\\r\\n$3\\r\\nSET\\r\\n$3\\r\\nfoo\\r\\n$3\\r\\nbar\\r\\n"
    result = decode_input(input_str)
    assert result == b"*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n"


def test_decode_input_invalid_escape():
    """Test decode_input with invalid escape sequence."""
    with pytest.raises(ValueError, match="Invalid escape sequence"):
        decode_input("*3\\x")


def test_parse_command_valid(runner):
    """Test parse command with valid RESP input."""
    input_str = "*3\\r\\n$3\\r\\nSET\\r\\n$3\\r\\nfoo\\r\\n$3\\r\\nbar\\r\\n"
    result = runner.invoke(cli, ["parse", input_str])
    assert result.exit_code == 0
    expected_output = "SET foo bar\n"
    assert result.output == expected_output


def test_parse_command_invalid(runner):
    """Test parse command with invalid RESP input."""
    input_str = "$3\\r\\nSET\\r\\n"
    result = runner.invoke(cli, ["parse", input_str])
    assert result.exit_code == 1
    assert "Expected a RESP array starting with *" in result.output


def test_serialize_command_valid(runner):
    """Test serialize command with valid input."""
    input_str = "foo"
    result = runner.invoke(cli, ["serialize", input_str])
    assert result.exit_code == 0
    expected_output = "$3\\r\\nfoo\\r\\n\n"
    assert result.output == expected_output


def test_serialize_command_quoted(runner):
    """Test serialize command with quoted input."""
    input_str = '"foo"'
    result = runner.invoke(cli, ["serialize", input_str])
    assert result.exit_code == 0
    expected_output = '$5\\r\\n"foo"\\r\\n\n'
    assert result.output == expected_output
