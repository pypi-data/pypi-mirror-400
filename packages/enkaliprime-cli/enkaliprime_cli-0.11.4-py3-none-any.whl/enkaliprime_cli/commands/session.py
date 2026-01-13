"""
Session management commands.

Create, list, and manage chat sessions.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from datetime import datetime
from typing import Optional
import keyring

console = Console()

SERVICE_NAME = "enkaliprime-cli"

app = typer.Typer(
    help="📝 Manage chat sessions",
    rich_markup_mode="rich",
)


def get_api_key():
    """Get API key from keyring."""
    return keyring.get_password(SERVICE_NAME, "api_key")


def create_client():
    """Create EnkaliPrime client with stored API key."""
    api_key = get_api_key()
    if not api_key:
        console.print("[red]❌ No API key configured.[/]")
        console.print("Run: [cyan]enkaliprime config set-api-key[/]")
        raise typer.Exit(1)

    from enkaliprime import EnkaliPrimeClient
    return EnkaliPrimeClient({
        "unified_api_key": api_key,
        "base_url": "https://sdk.enkaliprime.com"
    })


@app.command()
def create(
    agent_name: str = typer.Option(
        "CLI Assistant",
        "--name",
        "-n",
        help="Name for the AI agent",
    ),
    agent_avatar: Optional[str] = typer.Option(
        None,
        "--avatar",
        help="Avatar URL for the agent",
    ),
):
    """Create a new chat session."""
    try:
        client = create_client()
        session = client.create_session(
            agent_name=agent_name,
            agent_avatar=agent_avatar
        )

        console.print("[green]✅ Session created successfully![/]")
        console.print(f"Session ID: [cyan]{session.id}[/]")
        console.print(f"Agent: [cyan]{session.agent_name}[/]")
        console.print(f"Created: [cyan]{datetime.fromisoformat(session.start_time.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')}[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to create session: {str(e)}[/]")
        raise typer.Exit(1)


@app.command()
def current():
    """Show information about the current session."""
    try:
        client = create_client()
        session = client.current_session

        if not session:
            console.print("[yellow]⚠️  No active session.[/]")
            console.print("Create one with: [cyan]enkaliprime session create[/]")
            return

        console.print("[bold blue]📋 Current Session[/]")
        console.print(f"Session ID: [cyan]{session.id}[/]")
        console.print(f"Agent: [cyan]{session.agent_name}[/]")
        console.print(f"Status: [green]{'Active' if session.is_active else 'Ended'}[/]")

        if session.start_time:
            start_time = datetime.fromisoformat(session.start_time.replace('Z', '+00:00'))
            console.print(f"Started: [cyan]{start_time.strftime('%Y-%m-%d %H:%M:%S')}[/]")

        if session.end_time:
            end_time = datetime.fromisoformat(session.end_time.replace('Z', '+00:00'))
            console.print(f"Ended: [cyan]{end_time.strftime('%Y-%m-%d %H:%M:%S')}[/]")

        # Show conversation stats
        history = client.get_history()
        user_messages = len([m for m in history if m["role"] == "user"])
        ai_messages = len([m for m in history if m["role"] == "assistant"])

        console.print(f"Messages: [cyan]{user_messages} user, {ai_messages} AI[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to get session info: {str(e)}[/]")
        raise typer.Exit(1)


@app.command()
def end(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="End session without confirmation",
    ),
):
    """End the current chat session."""
    try:
        client = create_client()
        session = client.current_session

        if not session:
            console.print("[yellow]⚠️  No active session to end.[/]")
            return

        if not force:
            if not Confirm.ask(f"End session '{session.id}'?", default=False):
                console.print("[yellow]Operation cancelled.[/]")
                return

        ended_session = client.end_session()

        if ended_session:
            console.print("[green]✅ Session ended successfully![/]")
            console.print(f"Session ID: [cyan]{ended_session.id}[/]")

            if ended_session.end_time:
                end_time = datetime.fromisoformat(ended_session.end_time.replace('Z', '+00:00'))
                console.print(f"Ended at: [cyan]{end_time.strftime('%Y-%m-%d %H:%M:%S')}[/]")
        else:
            console.print("[yellow]⚠️  No session to end.[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to end session: {str(e)}[/]")
        raise typer.Exit(1)


@app.command()
def list():
    """List all sessions (shows current session info)."""
    try:
        client = create_client()
        session = client.current_session

        table = Table(title="[bold blue]📝 Chat Sessions[/]")
        table.add_column("Session ID", style="cyan")
        table.add_column("Agent", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Created", style="magenta")
        table.add_column("Messages", style="blue")

        if session:
            history = client.get_history()
            user_messages = len([m for m in history if m["role"] == "user"])

            start_time = datetime.fromisoformat(session.start_time.replace('Z', '+00:00'))
            status = "Active" if session.is_active else "Ended"

            table.add_row(
                session.id[:12] + "...",
                session.agent_name,
                status,
                start_time.strftime('%m/%d %H:%M'),
                str(user_messages)
            )

            console.print(table)
        else:
            console.print("[yellow]⚠️  No sessions found.[/]")
            console.print("Create one with: [cyan]enkaliprime session create[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to list sessions: {str(e)}[/]")
        raise typer.Exit(1)


@app.command()
def clear_history():
    """Clear conversation history for current session."""
    try:
        client = create_client()

        if not Confirm.ask("Clear conversation history?", default=False):
            console.print("[yellow]Operation cancelled.[/]")
            return

        client.clear_history()
        console.print("[green]✅ Conversation history cleared![/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to clear history: {str(e)}[/]")
        raise typer.Exit(1)
