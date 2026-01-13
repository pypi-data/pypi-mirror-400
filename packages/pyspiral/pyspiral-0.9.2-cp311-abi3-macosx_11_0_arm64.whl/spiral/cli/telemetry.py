import typer

from spiral.api.telemetry import IssueExportTokenResponse
from spiral.cli import CONSOLE, AsyncTyper, state

app = AsyncTyper(short_help="Client-side telemetry.")


@app.command(help="Issue new telemetry export token.")
def export(
    print_token: bool = typer.Option(False, "--print", help="Print the token instead of copying to clipboard."),
):
    res: IssueExportTokenResponse = state.spiral.api.telemetry.issue_export_token()

    if print_token:
        print(res.token)
    else:
        import pyperclip

        command = f"export SPIRAL_OTEL_TOKEN={res.token}"
        pyperclip.copy(command)

        CONSOLE.print("Export command copied to clipboard! Paste and run to set [green]SPIRAL_OTEL_TOKEN[/green].")
        CONSOLE.print("[dim]Token is valid for 1h.[/dim]")
