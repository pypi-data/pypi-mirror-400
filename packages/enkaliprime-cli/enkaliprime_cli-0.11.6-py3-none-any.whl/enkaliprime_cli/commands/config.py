"""
Configuration management commands.

Handles API key storage, settings, and configuration validation.
"""

import keyring
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from typing import Optional
import requests

from enkaliprime.type_guards import is_valid_api_key

console = Console()

# Keyring service name
SERVICE_NAME = "enkaliprime-cli"

app = typer.Typer(
    help="⚙️  Manage CLI configuration and API keys",
    rich_markup_mode="rich",
)


@app.command()
def set_api_key(
    api_key: Optional[str] = typer.Option(
        None,
        "--key",
        "-k",
        help="API key (if not provided, will prompt securely)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing API key without confirmation",
    ),
):
    """Set your EnkaliPrime API key securely."""
    try:
        # Check if key already exists
        existing_key = keyring.get_password(SERVICE_NAME, "api_key")
        if existing_key and not force:
            if not Confirm.ask("API key already exists. Overwrite?", default=False):
                console.print("[yellow]Operation cancelled.[/]")
                return

        # Get API key from argument or prompt
        if not api_key:
            api_key = Prompt.ask("Enter your EnkaliPrime API key", password=True)

        # Validate API key format
        if not is_valid_api_key(api_key):
            console.print("[red]❌ Invalid API key format. Should start with 'ek_bridge_'[/]")
            return

        # Store securely
        keyring.set_password(SERVICE_NAME, "api_key", api_key)

        # Mask the key for display
        masked_key = api_key[:15] + "..." + api_key[-4:] if len(api_key) > 20 else api_key

        console.print(f"[green]✅ API key set successfully: {masked_key}[/]")
        console.print("[dim]Your API key is stored securely using your system's keyring.[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to set API key: {str(e)}[/]")


@app.command()
def get_api_key():
    """Show current API key (masked for security)."""
    try:
        api_key = keyring.get_password(SERVICE_NAME, "api_key")

        if not api_key:
            console.print("[yellow]⚠️  No API key configured.[/]")
            console.print("Set one with: [cyan]enkaliprime config set-api-key[/]")
            return

        # Mask the key for display
        masked_key = api_key[:15] + "..." + api_key[-4:] if len(api_key) > 20 else api_key

        console.print(f"[green]API Key: {masked_key}[/]")

        # Validate the stored key
        if is_valid_api_key(api_key):
            console.print("[green]✅ Key format is valid[/]")
        else:
            console.print("[red]❌ Key format appears invalid[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to retrieve API key: {str(e)}[/]")


@app.command()
def remove_api_key(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Remove without confirmation",
    ),
):
    """Remove stored API key."""
    try:
        api_key = keyring.get_password(SERVICE_NAME, "api_key")

        if not api_key:
            console.print("[yellow]⚠️  No API key to remove.[/]")
            return

        if not force:
            masked_key = api_key[:15] + "..." + api_key[-4:] if len(api_key) > 20 else api_key
            if not Confirm.ask(f"Remove API key '{masked_key}'?", default=False):
                console.print("[yellow]Operation cancelled.[/]")
                return

        keyring.delete_password(SERVICE_NAME, "api_key")
        console.print("[green]✅ API key removed successfully.[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to remove API key: {str(e)}[/]")


@app.command()
def test_connection():
    """Test connection to EnkaliPrime API."""
    try:
        from enkaliprime import EnkaliPrimeClient

        api_key = keyring.get_password(SERVICE_NAME, "api_key")

        if not api_key:
            console.print("[red]❌ No API key configured.[/]")
            console.print("Set one with: [cyan]enkaliprime config set-api-key[/]")
            return

        console.print("🔗 Testing connection...")

        # Create client and test connection
        client = EnkaliPrimeClient({
            "unified_api_key": api_key,
            "base_url": "https://sdk.enkaliprime.com"
        })

        connection = client.get_connection()

        console.print("[green]✅ Connection successful![/]")
        console.print(f"Widget: [cyan]{connection.widget_name}[/]")
        console.print(f"Base URL: [cyan]{connection.base_url}[/]")
        console.print(f"Status: [green]{'Active' if connection.is_active else 'Inactive'}[/]")

    except Exception as e:
        console.print(f"[red]❌ Connection test failed: {str(e)}[/]")
        console.print("Check your API key and internet connection.")


@app.command()
def show():
    """Show current configuration."""
    try:
        panel_content = []

        # API Key status
        api_key = keyring.get_password(SERVICE_NAME, "api_key")
        if api_key:
            masked_key = api_key[:15] + "..." + api_key[-4:]
            panel_content.append(f"[green]API Key:[/] {masked_key}")
            panel_content.append(f"[green]Key Valid:[/] {'✅' if is_valid_api_key(api_key) else '❌'}")
        else:
            panel_content.append("[red]API Key: Not configured[/]")

        # Default settings
        panel_content.append("[blue]Base URL:[/] https://sdk.enkaliprime.com")

        panel = Panel(
            "\n".join(panel_content),
            title="[bold blue]EnkaliPrime CLI Configuration[/]",
            border_style="blue",
        )

        console.print(panel)

    except Exception as e:
        console.print(f"[red]❌ Failed to show configuration: {str(e)}[/]")


@app.command()
def set_ollama_model(
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Ollama model name (if not provided, will show available models to choose from)",
    ),
):
    """Set default Ollama model for local LLM usage."""
    try:
        # Check if Ollama is available
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code != 200:
                console.print("[red]❌ Ollama is not running or not accessible.[/]")
                console.print("Make sure Ollama is installed and running: [cyan]ollama serve[/]")
                return
        except requests.exceptions.RequestException:
            console.print("[red]❌ Cannot connect to Ollama.[/]")
            console.print("Make sure Ollama is installed and running: [cyan]ollama serve[/]")
            return

        available_models = []
        if response.status_code == 200:
            data = response.json()
            available_models = [m['name'] for m in data.get('models', [])]

        if not available_models:
            console.print("[yellow]⚠️  No models installed in Ollama.[/]")
            console.print("Install a model first:")
            console.print("  [cyan]ollama pull llama2[/]")
            console.print("  [cyan]ollama pull codellama[/]")
            return

        if not model:
            # Show available models and let user choose
            console.print("[blue]Available Ollama models:[/]")
            table = Table(box=None)
            table.add_column("#", style="cyan", justify="right")
            table.add_column("Model", style="white")
            table.add_column("Size", style="dim")

            for i, model_info in enumerate(data.get('models', []), 1):
                size = model_info.get('size', 0)
                size_gb = size / (1024**3) if size > 0 else 0
                table.add_row(str(i), model_info['name'], f"{size_gb:.1f}GB" if size_gb > 0 else "Unknown")

            console.print(table)

            while True:
                choice = Prompt.ask("Select model number (or enter model name directly)", default="1")
                try:
                    choice_num = int(choice) - 1
                    if 0 <= choice_num < len(available_models):
                        model = available_models[choice_num]
                        break
                    else:
                        console.print("[red]Invalid choice. Try again.[/]")
                except ValueError:
                    # User entered a model name directly
                    if choice in available_models:
                        model = choice
                        break
                    else:
                        console.print("[red]Model not found. Try again.[/]")
        else:
            # Validate provided model
            if model not in available_models:
                console.print(f"[red]❌ Model '{model}' not found in Ollama.[/]")
                console.print("Available models:")
                for m in available_models:
                    console.print(f"  [cyan]{m}[/]")
                return

        # Store the model
        keyring.set_password(SERVICE_NAME, "ollama_model", model)
        console.print(f"[green]✅ Default Ollama model set to: {model}[/]")
        console.print("Use [cyan]--local[/] flag with chat commands to use this model.")

    except Exception as e:
        console.print(f"[red]❌ Failed to set Ollama model: {str(e)}[/]")


@app.command()
def get_ollama_model():
    """Show current default Ollama model."""
    try:
        model = keyring.get_password(SERVICE_NAME, "ollama_model")

        if not model:
            console.print("[yellow]⚠️  No default Ollama model configured.[/]")
            console.print("Set one with: [cyan]enkaliprime config set-ollama-model[/]")
            return

        console.print(f"[green]Default Ollama Model: {model}[/]")

        # Check if Ollama is available and model exists
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                available_models = [m['name'] for m in response.json().get('models', [])]
                if model in available_models:
                    console.print("[green]✅ Model is available[/]")
                else:
                    console.print("[red]❌ Model not found in Ollama[/]")
                    console.print("Update with: [cyan]enkaliprime config set-ollama-model[/]")
            else:
                console.print("[yellow]⚠️  Cannot check Ollama status[/]")
        except:
            console.print("[yellow]⚠️  Ollama not accessible[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to get Ollama model: {str(e)}[/]")


@app.command()
def remove_ollama_model(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Remove without confirmation",
    ),
):
    """Remove default Ollama model configuration."""
    try:
        model = keyring.get_password(SERVICE_NAME, "ollama_model")

        if not model:
            console.print("[yellow]⚠️  No Ollama model to remove.[/]")
            return

        if not force:
            if not Confirm.ask(f"Remove default Ollama model '{model}'?", default=False):
                console.print("[yellow]Operation cancelled.[/]")
                return

        keyring.delete_password(SERVICE_NAME, "ollama_model")
        console.print("[green]✅ Default Ollama model removed.[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to remove Ollama model: {str(e)}[/]")


@app.command()
def show_ollama():
    """Show Ollama status and available models."""
    try:
        console.print("[blue]🔍 Checking Ollama status...[/]")

        # Check Ollama connection
        try:
            response = requests.get("http://localhost:11434/api/version", timeout=5)
            if response.status_code == 200:
                version = response.json().get('version', 'Unknown')
                console.print(f"[green]✅ Ollama is running (version: {version})[/]")
            else:
                console.print("[red]❌ Ollama responded but with error status[/]")
                return
        except requests.exceptions.RequestException:
            console.print("[red]❌ Cannot connect to Ollama[/]")
            console.print("Make sure Ollama is installed and running:")
            console.print("  [cyan]ollama serve[/]")
            return

        # Get models
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])

                if not models:
                    console.print("[yellow]⚠️  No models installed[/]")
                    console.print("Install some models:")
                    console.print("  [cyan]ollama pull llama2[/]")
                    console.print("  [cyan]ollama pull codellama[/]")
                    return

                # Show models table
                table = Table(title="🏠 Available Ollama Models", box=None)
                table.add_column("Model", style="cyan")
                table.add_column("Size", style="white", justify="right")
                table.add_column("Modified", style="dim")

                for model in models:
                    size = model.get('size', 0)
                    size_gb = size / (1024**3) if size > 0 else 0
                    modified = model.get('modified_at', 'Unknown')[:19]  # Truncate timestamp

                    table.add_row(
                        model['name'],
                        f"{size_gb:.1f}GB" if size_gb > 0 else "Unknown",
                        modified
                    )

                console.print(table)

                # Show current default
                default_model = keyring.get_password(SERVICE_NAME, "ollama_model")
                if default_model:
                    if any(m['name'] == default_model for m in models):
                        console.print(f"[green]📌 Default model: {default_model}[/]")
                    else:
                        console.print(f"[red]⚠️  Default model '{default_model}' not found[/]")

            else:
                console.print("[red]❌ Failed to get model list[/]")

        except Exception as e:
            console.print(f"[red]❌ Error getting models: {str(e)}[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to check Ollama: {str(e)}[/]")


@app.command()
def set_system_prompt():
    """Set a custom system prompt for local LLMs."""
    try:
        console.print("[blue]📝 Configure System Prompt[/]")
        console.print("This prompt will define how your local AI behaves and responds.")
        console.print()

        # Show current prompt if any
        current_prompt = keyring.get_password(SERVICE_NAME, "system_prompt")
        if current_prompt:
            console.print("[yellow]Current system prompt:[/]")
            console.print(f"[dim]{current_prompt}[/]")
            console.print()

        # Get new prompt
        console.print("Enter your custom system prompt (press Enter twice to finish):")
        console.print("[dim]Example: 'You are a helpful coding assistant. Always provide clear, concise answers with code examples.'[/]")
        console.print()

        lines = []
        while True:
            try:
                line = input()
                if not line and lines:  # Empty line and we have content
                    break
                lines.append(line)
            except (EOFError, KeyboardInterrupt):
                console.print("[yellow]Cancelled.[/]")
                return

        new_prompt = '\n'.join(lines).strip()

        if not new_prompt:
            console.print("[yellow]No prompt entered. Keeping current setting.[/]")
            return

        # Store the prompt
        keyring.set_password(SERVICE_NAME, "system_prompt", new_prompt)

        # Show preview
        console.print("[green]✅ System prompt updated![/]")
        console.print()
        console.print("[blue]Preview:[/]")
        console.print(f"[dim]{new_prompt}[/]")
        console.print()
        console.print("[green]This will be used with all --local chat commands.[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to set system prompt: {str(e)}[/]")


@app.command()
def get_system_prompt():
    """Show the current system prompt."""
    try:
        prompt = keyring.get_password(SERVICE_NAME, "system_prompt")

        if not prompt:
            console.print("[yellow]⚠️  No custom system prompt configured.[/]")
            console.print("Set one with: [cyan]enkaliprime config set-system-prompt[/]")
            console.print()
            console.print("[dim]Default behavior: AI will use its built-in personality[/]")
            return

        console.print("[green]Current System Prompt:[/]")
        console.print(f"[dim]{prompt}[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to get system prompt: {str(e)}[/]")


@app.command()
def remove_system_prompt(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Remove without confirmation",
    ),
):
    """Remove the custom system prompt."""
    try:
        prompt = keyring.get_password(SERVICE_NAME, "system_prompt")

        if not prompt:
            console.print("[yellow]⚠️  No system prompt to remove.[/]")
            return

        if not force:
            console.print("[yellow]Current prompt:[/]")
            console.print(f"[dim]{prompt}[/]")
            console.print()
            if not Confirm.ask("Remove this system prompt?", default=False):
                console.print("[yellow]Operation cancelled.[/]")
                return

        keyring.delete_password(SERVICE_NAME, "system_prompt")
        console.print("[green]✅ System prompt removed. AI will use default behavior.[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to remove system prompt: {str(e)}[/]")


@app.command()
def set_ai_personality():
    """Set a custom personality and name for your local AI."""
    try:
        console.print("[blue]🎭 Configure AI Personality[/]")
        console.print("Give your AI a name and define its personality traits.")
        console.print()

        # Show current personality if any
        current_name = keyring.get_password(SERVICE_NAME, "ai_name")
        current_personality = keyring.get_password(SERVICE_NAME, "ai_personality")

        if current_name or current_personality:
            console.print("[yellow]Current personality:[/]")
            if current_name:
                console.print(f"[dim]Name: {current_name}[/]")
            if current_personality:
                console.print(f"[dim]Traits: {current_personality}[/]")
            console.print()

        # Get AI name
        console.print("What should your AI be called?")
        console.print("[dim]Example: 'CodeBuddy', 'TechGuru', 'AI Assistant'[/]")
        ai_name = input("AI Name: ").strip()

        if not ai_name:
            console.print("[yellow]No name entered. Keeping current setting.[/]")
            return

        # Get personality traits
        console.print()
        console.print("Describe your AI's personality and behavior:")
        console.print("[dim]Example: 'helpful, patient, focuses on practical solutions, loves explaining concepts'[/]")
        personality = input("Personality: ").strip()

        # Store the settings
        keyring.set_password(SERVICE_NAME, "ai_name", ai_name)
        if personality:
            keyring.set_password(SERVICE_NAME, "ai_personality", personality)

        # Show summary
        console.print()
        console.print("[green]✅ AI Personality configured![/]")
        console.print(f"[blue]Name:[/] {ai_name}")
        if personality:
            console.print(f"[blue]Personality:[/] {personality}")

        console.print()
        console.print("[green]Your AI will now respond with this personality in --local chat sessions![/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to set AI personality: {str(e)}[/]")


@app.command()
def get_ai_personality():
    """Show the current AI personality configuration."""
    try:
        name = keyring.get_password(SERVICE_NAME, "ai_name")
        personality = keyring.get_password(SERVICE_NAME, "ai_personality")

        if not name and not personality:
            console.print("[yellow]⚠️  No AI personality configured.[/]")
            console.print("Set one with: [cyan]enkaliprime config set-ai-personality[/]")
            return

        console.print("[green]AI Personality Configuration:[/]")
        if name:
            console.print(f"[blue]Name:[/] {name}")
        if personality:
            console.print(f"[blue]Personality:[/] {personality}")

        # Show how it will be used
        system_prompt = keyring.get_password(SERVICE_NAME, "system_prompt")
        if system_prompt or personality:
            console.print()
            console.print("[cyan]This will be combined with your system prompt for rich AI behavior.[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to get AI personality: {str(e)}[/]")


@app.command()
def remove_ai_personality(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Remove without confirmation",
    ),
):
    """Remove the custom AI personality."""
    try:
        name = keyring.get_password(SERVICE_NAME, "ai_name")
        personality = keyring.get_password(SERVICE_NAME, "ai_personality")

        if not name and not personality:
            console.print("[yellow]⚠️  No AI personality to remove.[/]")
            return

        if not force:
            console.print("[yellow]Current personality:[/]")
            if name:
                console.print(f"[dim]Name: {name}[/]")
            if personality:
                console.print(f"[dim]Personality: {personality}[/]")
            console.print()
            if not Confirm.ask("Remove this AI personality?", default=False):
                console.print("[yellow]Operation cancelled.[/]")
                return

        # Remove both settings
        try:
            keyring.delete_password(SERVICE_NAME, "ai_name")
        except:
            pass
        try:
            keyring.delete_password(SERVICE_NAME, "ai_personality")
        except:
            pass

        console.print("[green]✅ AI personality removed. AI will use default behavior.[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to remove AI personality: {str(e)}[/]")


@app.command()
def show_behavior():
    """Show current AI behavior configuration."""
    try:
        console.print("[blue]🤖 AI Behavior Configuration[/]")
        console.print()

        # System prompt
        system_prompt = keyring.get_password(SERVICE_NAME, "system_prompt")
        if system_prompt:
            console.print("[green]📝 System Prompt:[/]")
            console.print(f"[dim]{system_prompt}[/]")
            console.print()
        else:
            console.print("[yellow]📝 System Prompt: Not configured[/]")
            console.print("[dim]AI will use its default behavior[/]")
            console.print()

        # AI Personality
        ai_name = keyring.get_password(SERVICE_NAME, "ai_name")
        ai_personality = keyring.get_password(SERVICE_NAME, "ai_personality")

        if ai_name or ai_personality:
            console.print("[green]🎭 AI Personality:[/]")
            if ai_name:
                console.print(f"[dim]Name: {ai_name}[/]")
            if ai_personality:
                console.print(f"[dim]Traits: {ai_personality}[/]")
            console.print()
        else:
            console.print("[yellow]🎭 AI Personality: Not configured[/]")
            console.print("[dim]AI will use generic responses[/]")
            console.print()

        # Ollama model
        ollama_model = keyring.get_password(SERVICE_NAME, "ollama_model")
        if ollama_model:
            console.print(f"[green]🏠 Default Model: {ollama_model}[/]")
        else:
            console.print("[yellow]🏠 Default Model: Not configured[/]")

        # Cloud API key
        cloud_api_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")
        if cloud_api_key:
            masked_key = cloud_api_key[:8] + "..." + cloud_api_key[-4:] if len(cloud_api_key) > 12 else cloud_api_key
            console.print(f"[green]☁️  Cloud API Key: {masked_key}[/]")
        else:
            console.print("[yellow]☁️  Cloud API Key: Not configured[/]")

        # Default cloud model
        default_cloud_model = keyring.get_password(SERVICE_NAME, "default_cloud_model")
        if default_cloud_model:
            console.print(f"[green]☁️  Default Cloud Model: {default_cloud_model}[/]")
        else:
            console.print("[yellow]☁️  Default Cloud Model: Not configured (uses gpt-oss:120b)[/]")

        # Global default model/provider
        default_provider = keyring.get_password(SERVICE_NAME, "default_provider")
        default_model = keyring.get_password(SERVICE_NAME, "default_model")

        if default_provider:
            if default_provider == "remote":
                console.print("[green]🎯 Global Default: EnkaliPrime Assistant (Remote)[/]")
            elif default_provider == "ollama" and default_model:
                console.print(f"[green]🎯 Global Default: {default_model} (Local Ollama)[/]")
            elif default_provider == "cloud" and default_model:
                console.print(f"[green]🎯 Global Default: {default_model} (Cloud)[/]")
            else:
                console.print(f"[green]🎯 Global Default Provider: {default_provider.title()}[/]")
        else:
            console.print("[yellow]🎯 Global Default: Not configured (auto-detect)[/]")

        console.print()
        console.print("[cyan]💡 Configure with:[/]")
        console.print("[dim]• enkaliprime config set-system-prompt[/]")
        console.print("[dim]• enkaliprime config set-ai-personality[/]")
        console.print("[dim]• enkaliprime config set-ollama-model[/]")
        console.print("[dim]• enkaliprime config set-ollama-cloud-key[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to show behavior configuration: {str(e)}[/]")


@app.command()
def reset_ai_behavior(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Reset without confirmation",
    ),
):
    """Reset AI behavior to defaults (removes system prompt and personality)."""
    try:
        # Check what's currently configured
        system_prompt = keyring.get_password(SERVICE_NAME, "system_prompt")
        ai_name = keyring.get_password(SERVICE_NAME, "ai_name")
        ai_personality = keyring.get_password(SERVICE_NAME, "ai_personality")

        has_config = system_prompt or ai_name or ai_personality

        if not has_config:
            console.print("[yellow]⚠️  No AI behavior configuration to reset.[/]")
            console.print("[dim]AI is already using default behavior.[/]")
            return

        if not force:
            console.print("[yellow]Current AI behavior configuration:[/]")
            if system_prompt:
                console.print(f"[dim]• System Prompt: {system_prompt[:50]}...[/]")
            if ai_name:
                console.print(f"[dim]• AI Name: {ai_name}[/]")
            if ai_personality:
                console.print(f"[dim]• Personality: {ai_personality}[/]")
            console.print()
            if not Confirm.ask("Reset all AI behavior to defaults?", default=False):
                console.print("[yellow]Operation cancelled.[/]")
                return

        # Reset all AI behavior settings
        reset_count = 0

        try:
            if keyring.get_password(SERVICE_NAME, "system_prompt"):
                keyring.delete_password(SERVICE_NAME, "system_prompt")
                reset_count += 1
        except:
            pass

        try:
            if keyring.get_password(SERVICE_NAME, "ai_name"):
                keyring.delete_password(SERVICE_NAME, "ai_name")
                reset_count += 1
        except:
            pass

        try:
            if keyring.get_password(SERVICE_NAME, "ai_personality"):
                keyring.delete_password(SERVICE_NAME, "ai_personality")
                reset_count += 1
        except:
            pass

        console.print(f"[green]✅ AI behavior reset to defaults![/]")
        console.print(f"[dim]Removed {reset_count} configuration settings.[/]")
        console.print()
        console.print("[green]Your local AI will now use default behavior in --local chat sessions.[/]")

        # Show next steps
        console.print()
        console.print("[cyan]💡 To customize again:[/]")
        console.print("[dim]• enkaliprime config set-system-prompt[/]")
        console.print("[dim]• enkaliprime config set-ai-personality[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to reset AI behavior: {str(e)}[/]")


@app.command()
def set_ollama_cloud_key(
    api_key: Optional[str] = typer.Option(
        None,
        "--key",
        "-k",
        help="Ollama cloud API key (if not provided, will prompt securely)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing API key without confirmation",
    ),
):
    """Set your Ollama cloud API key for accessing cloud models."""
    try:
        # Check if key already exists
        existing_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")
        if existing_key and not force:
            if not Confirm.ask("Ollama cloud API key already exists. Overwrite?", default=False):
                console.print("[yellow]Operation cancelled.[/]")
                return

        # Get API key from argument or prompt
        if not api_key:
            console.print("Get your API key from: https://ollama.com/settings/keys")
            api_key = Prompt.ask("Enter your Ollama cloud API key", password=True)

        # Basic validation
        if not api_key or len(api_key.strip()) == 0:
            console.print("[red]❌ API key cannot be empty[/]")
            return

        # Store securely
        keyring.set_password(SERVICE_NAME, "ollama_cloud_api_key", api_key.strip())

        # Mask the key for display
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else api_key

        console.print(f"[green]✅ Ollama cloud API key set successfully: {masked_key}[/]")
        console.print("[dim]Your API key is stored securely using your system's keyring.[/]")
        console.print()
        console.print("[green]You can now use --cloud flag with chat commands![/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to set Ollama cloud API key: {str(e)}[/]")


@app.command()
def get_ollama_cloud_key():
    """Show current Ollama cloud API key (masked for security)."""
    try:
        api_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")

        if not api_key:
            console.print("[yellow]⚠️  No Ollama cloud API key configured.[/]")
            console.print("Set one with: [cyan]enkaliprime config set-ollama-cloud-key[/]")
            console.print("Get your key from: https://ollama.com/settings/keys")
            return

        # Mask the key for display
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else api_key

        console.print(f"[green]Ollama Cloud API Key: {masked_key}[/]")

        # Test the key
        try:
            import requests
            response = requests.get(
                "https://ollama.com/api/tags",
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=10
            )
            if response.status_code == 200:
                console.print("[green]✅ Key is valid and working[/]")
            else:
                console.print("[red]❌ Key appears invalid[/]")
        except:
            console.print("[yellow]⚠️  Cannot test key connectivity[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to retrieve Ollama cloud API key: {str(e)}[/]")


@app.command()
def remove_ollama_cloud_key(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Remove without confirmation",
    ),
):
    """Remove stored Ollama cloud API key."""
    try:
        api_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")

        if not api_key:
            console.print("[yellow]⚠️  No Ollama cloud API key to remove.[/]")
            return

        if not force:
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else api_key
            if not Confirm.ask(f"Remove Ollama cloud API key '{masked_key}'?", default=False):
                console.print("[yellow]Operation cancelled.[/]")
                return

        keyring.delete_password(SERVICE_NAME, "ollama_cloud_api_key")
        console.print("[green]✅ Ollama cloud API key removed successfully.[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to remove Ollama cloud API key: {str(e)}[/]")


@app.command()
def show_cloud():
    """Show Ollama cloud status and available models."""
    try:
        console.print("[blue]☁️  Checking Ollama Cloud status...[/]")

        # Check API key
        api_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")
        if not api_key:
            console.print("[red]❌ No Ollama cloud API key configured[/]")
            console.print("Set one with: [cyan]enkaliprime config set-ollama-cloud-key[/]")
            console.print("Get your key from: https://ollama.com/settings/keys")
            return

        console.print("[green]✅ API key is configured[/]")

        # Test connection and get models
        try:
            response = requests.get(
                "https://ollama.com/api/tags",
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=10
            )

            if response.status_code == 200:
                console.print("[green]✅ Cloud API connection successful[/]")

                data = response.json()
                models = data.get('models', [])

                if not models:
                    console.print("[yellow]⚠️  No cloud models available[/]")
                    return

                # Show models table
                table = Table(title="☁️ Available Ollama Cloud Models", box=None)
                table.add_column("Model", style="cyan")
                table.add_column("Size", style="white", justify="right")
                table.add_column("Status", style="green")

                for model in models:
                    size = model.get('size', 0)
                    size_gb = size / (1024**3) if size > 0 else 0

                    # Cloud models are typically larger
                    status = "Available" if size_gb > 1 else "Available"

                    table.add_row(
                        model['name'],
                        f"{size_gb:.1f}GB" if size_gb > 0 else "Unknown",
                        status
                    )

                console.print(table)
                console.print()
                console.print("[cyan]💡 Usage:[/]")
                console.print("[dim]• enkaliprime chat interactive --cloud[/]")
                console.print("[dim]• enkaliprime chat ask 'Hello' --cloud --model gpt-oss:120b[/]")

            else:
                console.print(f"[red]❌ API error: {response.status_code}[/]")
                if response.status_code == 401:
                    console.print("[red]Invalid API key. Please check and update your key.[/]")

        except requests.exceptions.RequestException as e:
            console.print(f"[red]❌ Connection failed: {str(e)}[/]")
            console.print("Check your internet connection and API key.")

    except Exception as e:
        console.print(f"[red]❌ Failed to check Ollama cloud: {str(e)}[/]")


@app.command()
def set_default_cloud_model(
    model: str = typer.Argument(None, help="Cloud model name to set as default"),
):
    """Set your default cloud model for --cloud flag usage."""
    try:
        # If no model specified, show available models and let user choose
        if not model:
            console.print("[blue]☁️  Select Default Cloud Model[/]")
            console.print("Choose from available Ollama cloud models:")
            console.print()

            # Check if API key is configured
            api_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")
            if not api_key:
                console.print("[red]❌ No cloud API key configured.[/]")
                console.print("Set one with: [cyan]enkaliprime config set-ollama-cloud-key[/]")
                return

            # Get available models
            try:
                response = requests.get(
                    "https://ollama.com/api/tags",
                    headers={'Authorization': f'Bearer {api_key}'},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    models = data.get('models', [])

                    if not models:
                        console.print("[yellow]⚠️  No cloud models available[/]")
                        return

                    # Show models table
                    from rich.table import Table
                    table = Table(title="Available Cloud Models", box=None)
                    table.add_column("#", style="cyan", no_wrap=True)
                    table.add_column("Model", style="magenta", no_wrap=True)
                    table.add_column("Size", style="green", no_wrap=True)
                    table.add_column("Description", style="white")

                    model_options = []
                    for i, model_info in enumerate(models[:10]):  # Limit to first 10
                        name = model_info['name']
                        size_bytes = model_info.get('size', 0)
                        size_gb = f"{size_bytes / (1024**3):.1f}GB" if size_bytes > 0 else "Unknown"

                        # Add some helpful descriptions
                        desc = ""
                        if "gpt-oss" in name:
                            desc = "Large GPT-style model"
                        elif "llama" in name.lower():
                            desc = "Meta Llama model"
                        elif "codellama" in name.lower():
                            desc = "Code-focused model"
                        else:
                            desc = "General purpose AI"

                        table.add_row(str(i + 1), name, size_gb, desc)
                        model_options.append(name)

                    console.print(table)
                    console.print()

                    # Get user selection
                    while True:
                        selection = Prompt.ask("Select model number or enter model name directly").strip()

                        # Try to parse as number
                        try:
                            idx = int(selection) - 1
                            if 0 <= idx < len(model_options):
                                model = model_options[idx]
                                break
                        except ValueError:
                            pass

                        # Check if it's a direct model name
                        if selection in model_options:
                            model = selection
                            break

                        console.print("[red]❌ Invalid selection. Please try again.[/]")

                else:
                    console.print(f"[red]❌ Failed to fetch models: {response.status_code}[/]")
                    return

            except Exception as e:
                console.print(f"[red]❌ Failed to fetch available models: {str(e)}[/]")
                return

        # Validate the model exists (basic check)
        if model:
            # Store the default model
            keyring.set_password(SERVICE_NAME, "default_cloud_model", model)

            console.print(f"[green]✅ Default cloud model set to: {model}[/]")
            console.print()
            console.print("[green]Now you can use --cloud flag without specifying a model![/]")
            console.print(f"[dim]Example: enkaliprime chat interactive --cloud[/]")
        else:
            console.print("[red]❌ No model selected[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to set default cloud model: {str(e)}[/]")


@app.command()
def get_default_cloud_model():
    """Show the current default cloud model."""
    try:
        model = keyring.get_password(SERVICE_NAME, "default_cloud_model")

        if not model:
            console.print("[yellow]⚠️  No default cloud model configured.[/]")
            console.print("Set one with: [cyan]enkaliprime config set-default-cloud-model[/]")
            console.print()
            console.print("[dim]Cloud commands will use 'gpt-oss:120b' as default[/]")
            return

        console.print(f"[green]Default Cloud Model: {model}[/]")

        # Check if API key is configured
        api_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")
        if api_key:
            console.print("[green]✅ Cloud API key is configured[/]")
        else:
            console.print("[yellow]⚠️  Cloud API key not configured[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to get default cloud model: {str(e)}[/]")


@app.command()
def remove_default_cloud_model(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Remove without confirmation",
    ),
):
    """Remove the default cloud model setting."""
    try:
        model = keyring.get_password(SERVICE_NAME, "default_cloud_model")

        if not model:
            console.print("[yellow]⚠️  No default cloud model to remove.[/]")
            return

        if not force:
            if not Confirm.ask(f"Remove default cloud model '{model}'?", default=False):
                console.print("[yellow]Operation cancelled.[/]")
                return

        keyring.delete_password(SERVICE_NAME, "default_cloud_model")
        console.print("[green]✅ Default cloud model removed.[/]")
        console.print("[dim]Cloud commands will use 'gpt-oss:120b' as default[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to remove default cloud model: {str(e)}[/]")


@app.command()
def set_default_model():
    """Set your default AI model from all available providers."""
    try:
        console.print("[blue]🎯 Select Default AI Model[/]")
        console.print("Choose from all available models across all providers:")
        console.print()

        available_options = []
        option_number = 1

        # Local Ollama models
        try:
            ollama_url = "http://localhost:11434/api/tags"
            response = requests.get(ollama_url, timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                local_models = models_data.get("models", [])

                if local_models:
                    console.print("[green]🏠 Local Ollama Models:[/]")
                    for model_info in local_models[:5]:  # Limit to first 5
                        name = model_info["name"].split(":")[0]  # Remove tag
                        size_bytes = model_info["size"]
                        size_gb = f"{size_bytes / (1024**3):.1f}GB"
                        console.print(f"[dim]{option_number}.[/] {name} [dim]({size_gb}, Local)[/]")
                        available_options.append(('ollama', name))
                        option_number += 1
                    console.print()
        except:
            pass  # Ollama not available, skip

        # Cloud models
        cloud_api_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")
        if cloud_api_key:
            try:
                response = requests.get(
                    "https://ollama.com/api/tags",
                    headers={'Authorization': f'Bearer {cloud_api_key}'},
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    cloud_models = data.get('models', [])

                    if cloud_models:
                        console.print("[magenta]☁️  Cloud Models:[/]")
                        for model_info in cloud_models[:5]:  # Limit to first 5
                            name = model_info['name']
                            size_bytes = model_info.get('size', 0)
                            size_gb = f"{size_bytes / (1024**3):.1f}GB" if size_bytes > 0 else "Unknown"

                            # Add helpful descriptions
                            desc = ""
                            if "gpt-oss" in name:
                                desc = "Large GPT-style"
                            elif "llama" in name.lower():
                                desc = "Meta Llama"
                            elif "codellama" in name.lower():
                                desc = "Code-focused"
                            else:
                                desc = "General AI"

                            console.print(f"[dim]{option_number}.[/] {name} [dim]({size_gb}, Cloud, {desc})[/]")
                            available_options.append(('cloud', name))
                            option_number += 1
                        console.print()
            except:
                pass

        # Remote EnkaliPrime (always available)
        console.print("[cyan]🌐 Remote Models:[/]")
        console.print(f"[dim]{option_number}.[/] EnkaliPrime Assistant [dim](Cloud API, Remote)[/]")
        available_options.append(('remote', 'enkali-prime'))
        option_number += 1
        console.print()

        if not available_options:
            console.print("[yellow]⚠️  No models available. Please check your connections:[/]")
            console.print("[dim]• Start Ollama service for local models[/]")
            console.print("[dim]• Configure cloud API key for cloud models[/]")
            return

        # Get user selection
        while True:
            try:
                selection = int(Prompt.ask("Select model number")) - 1
                if 0 <= selection < len(available_options):
                    provider, model = available_options[selection]
                    break
                else:
                    console.print("[red]❌ Invalid selection. Please enter a valid number.[/]")
            except ValueError:
                console.print("[red]❌ Please enter a number.[/]")
            except (EOFError, KeyboardInterrupt):
                console.print("[yellow]Operation cancelled.[/]")
                return

        # Set the default based on provider
        if provider == 'ollama':
            keyring.set_password(SERVICE_NAME, "default_provider", "ollama")
            keyring.set_password(SERVICE_NAME, "default_model", model)
            console.print(f"[green]✅ Default model set to: {model} (Local Ollama)[/]")

        elif provider == 'cloud':
            keyring.set_password(SERVICE_NAME, "default_provider", "cloud")
            keyring.set_password(SERVICE_NAME, "default_model", model)
            console.print(f"[green]✅ Default model set to: {model} (Cloud)[/]")

        else:  # remote
            keyring.set_password(SERVICE_NAME, "default_provider", "remote")
            keyring.delete_password(SERVICE_NAME, "default_model")  # Remote doesn't need specific model
            console.print("[green]✅ Default model set to: EnkaliPrime Assistant (Remote)[/]")

        console.print()
        console.print("[green]Now you can simply run:[/]")
        console.print("[dim]enkaliprime chat interactive[/]")
        console.print("[dim]enkaliprime chat ask 'your question'[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to set default model: {str(e)}[/]")


@app.command()
def get_default_model():
    """Show the current default AI model and provider."""
    try:
        provider = keyring.get_password(SERVICE_NAME, "default_provider")
        model = keyring.get_password(SERVICE_NAME, "default_model")

        if not provider:
            console.print("[yellow]⚠️  No default model configured.[/]")
            console.print("Set one with: [cyan]enkaliprime config set-default-model[/]")
            console.print()
            console.print("[dim]Commands will auto-detect available providers[/]")
            return

        if provider == 'remote':
            console.print("[green]Default Model: EnkaliPrime Assistant (Remote)[/]")
        elif provider == 'ollama':
            if model:
                console.print(f"[green]Default Model: {model} (Local Ollama)[/]")
                # Check if Ollama is running
                try:
                    response = requests.get("http://localhost:11434/api/tags", timeout=3)
                    if response.status_code == 200:
                        console.print("[green]✅ Ollama service is running[/]")
                    else:
                        console.print("[yellow]⚠️  Ollama service may not be running[/]")
                except:
                    console.print("[yellow]⚠️  Cannot connect to Ollama service[/]")
            else:
                console.print("[yellow]Default Provider: Local Ollama (no specific model)[/]")
        elif provider == 'cloud':
            if model:
                console.print(f"[green]Default Model: {model} (Cloud)[/]")
                # Check cloud API key
                cloud_api_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")
                if cloud_api_key:
                    console.print("[green]✅ Cloud API key is configured[/]")
                else:
                    console.print("[red]❌ Cloud API key not configured[/]")
            else:
                console.print("[yellow]Default Provider: Cloud (no specific model)[/]")
        else:
            console.print(f"[yellow]Unknown provider: {provider}[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to get default model: {str(e)}[/]")


@app.command()
def remove_default_model(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Remove without confirmation",
    ),
):
    """Remove the default model setting."""
    try:
        provider = keyring.get_password(SERVICE_NAME, "default_provider")

        if not provider:
            console.print("[yellow]⚠️  No default model to remove.[/]")
            return

        if not force:
            if not Confirm.ask("Remove default model configuration?", default=False):
                console.print("[yellow]Operation cancelled.[/]")
                return

        # Remove default settings
        try:
            keyring.delete_password(SERVICE_NAME, "default_provider")
        except:
            pass
        try:
            keyring.delete_password(SERVICE_NAME, "default_model")
        except:
            pass

        console.print("[green]✅ Default model removed.[/]")
        console.print("[dim]Commands will auto-detect available providers[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to remove default model: {str(e)}[/]")
