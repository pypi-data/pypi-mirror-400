import click
from .parser import RespParser, RespSerializer


def decode_input(resp_string: str) -> bytes:
    """Convert CLI RESP string with literal escapes to bytes."""
    try:
        return bytes(resp_string, "utf-8").decode("unicode_escape").encode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"Invalid escape sequence in input: {e}")


@click.group()
def cli():
    pass


@cli.command()
@click.argument("resp_string")
def parse(resp_string: str) -> str:
    try:
        rp = RespParser()
        resp_string_bytes = decode_input(resp_string)
        parsed_resp_list = rp.parse(resp_string_bytes)
        parsed_command_str = " ".join(
            [item.decode() if item is not None else "None" for item in parsed_resp_list]
        )
        click.echo(parsed_command_str)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("resp_string")
def serialize(resp_string: str) -> str:
    try:
        rp = RespSerializer()
        serialized = rp.serialize(resp_string).decode("utf-8")
        escaped_serialized = serialized.replace("\r\n", "\\r\\n")
        click.echo(escaped_serialized)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
