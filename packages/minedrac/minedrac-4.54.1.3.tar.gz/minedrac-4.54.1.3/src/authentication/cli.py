import typer

from data import session

authentication_app = typer.Typer(
    help="Allows users to log in to the application and obtain information about a token"
)


@authentication_app.command("authenticate", help="Allows users to log in")
def authenticate_cli(
    authenticator: str = typer.Option(
        "db",
        "-a",
        "--authenticator",
        help="Plugin authentication. it can be db or esrf. Default is db",
    ),
    username: str = typer.Option(..., "-u", "--username", help="ICAT username"),
    password: str = typer.Option(..., "-p", "--password", help="ICAT password"),
):
    """Retrieve investigations by session_id."""
    session_response = session.get_session(authenticator, username, password)
    typer.echo(session_response)


@authentication_app.command("info", help="Provides token information.")
def get_session_info(
    token: str = typer.Option(..., "-t", "--token", help="ICAT token"),
):
    """Retrieve investigations by session_id."""
    session_response = session.get_info(token)
    typer.echo(session_response)
