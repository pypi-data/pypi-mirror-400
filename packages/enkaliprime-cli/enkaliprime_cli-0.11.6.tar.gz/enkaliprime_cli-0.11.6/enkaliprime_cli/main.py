"""
Main CLI application for EnkaliPrime.

Provides commands for interactive chat, configuration management, and session handling.
"""

import typer
from typing import Optional
from rich.console import Console

from . import __app_name__, __version__
from .commands import chat, config, session
from .ui import console
from .banner import show_startup_banner
from .menu import show_interactive_menu

# Create the main Typer app
app = typer.Typer(
    name=__app_name__,
    help="🤖 EnkaliPrime CLI - AI Chat from your terminal",
    add_completion=True,
    rich_markup_mode="rich",
    invoke_without_command=True,
)

# Add subcommands
app.add_typer(chat.app, name="chat", help="💬 Interactive chat with AI")
app.add_typer(config.app, name="config", help="⚙️  Manage configuration and API keys")
app.add_typer(session.app, name="session", help="📝 Manage chat sessions")



from .ui import Header, console, print_success, print_error, COLOR_PRIMARY

# ... (imports)

@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version information",
        is_eager=True,
    ),
):
    """EnkaliPrime CLI - AI Chat from your terminal."""
    if version:
        Header.draw()
        raise typer.Exit()

    # Show banner and menu when no command is provided
    if ctx.invoked_subcommand is None:
        show_startup_banner()
        show_interactive_menu()
        ctx.exit()


@app.command()
def info():
    """Show information about the CLI and SDK."""
    Header.draw()
    
    console.print(f"\n[bold {COLOR_PRIMARY}]Features:[/]")
    console.print("* Interactive AI chat with web search")
    console.print("* Multiple AI providers (remote, local, cloud)")
    console.print("* Instant AI responses")
    console.print("* Secure API key management")
    console.print("* Session management")
    console.print("* Rich terminal output")
    console.print("* Interactive commands (/web, /status, /help)")
    
    console.print(f"\n[bold {COLOR_PRIMARY}]Get started:[/]")
    console.print("1. Configure your API key: [cyan]enkaliprime config set-api-key[/]")
    console.print("2. Start chatting: [cyan]enkaliprime chat[/]")
    console.print("\n[dim]For more help, use: enkaliprime --help[/]")



if __name__ == "__main__":
    app()
