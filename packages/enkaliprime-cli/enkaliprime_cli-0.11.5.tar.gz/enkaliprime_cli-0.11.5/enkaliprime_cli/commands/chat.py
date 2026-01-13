"""
Interactive chat commands.

Provides real-time chat interface with AI using the EnkaliPrime SDK.
"""

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.table import Table
from rich import box
import keyring
from typing import Optional, Dict, Any
import requests
import json

from ..ui import console, Header, cyber_panel, print_success, print_error, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, COLOR_DIM
from ..code_utils import process_ai_response, copy_code_block, copy_all_code, show_code_blocks

SERVICE_NAME = "enkaliprime-cli"


class LocalLLMProvider:
    """Base class for local LLM providers."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = []

    def is_available(self) -> bool:
        """Check if the local provider is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> list:
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []

    def generate(self, prompt: str, model: str = "llama2", system_prompt: str = None, ai_name: str = None, ai_personality: str = None, **kwargs) -> str:
        """Generate text using the local LLM."""
        try:
            # Build system message from configuration
            system_parts = []

            if ai_name:
                system_parts.append(f"You are {ai_name}.")

            if ai_personality:
                system_parts.append(f"Your personality: {ai_personality}")

            if system_prompt:
                system_parts.append(system_prompt)

            # Combine all system instructions
            full_system = " ".join(system_parts) if system_parts else None

            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }

            # Add system prompt if configured
            if full_system:
                payload["system"] = full_system

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            if response.status_code == 200:
                return response.json().get('response', '')
        except Exception as e:
            raise Exception(f"Local LLM generation failed: {str(e)}")
        return ""


class OllamaProvider(LocalLLMProvider):
    """Ollama-specific implementation."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__(base_url)


class OllamaCloudProvider:
    """Ollama Cloud API implementation."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or self._get_api_key()
        self.base_url = "https://ollama.com"
        self.available_models = []

    def _get_api_key(self):
        """Get API key from keyring."""
        return keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")

    def is_available(self) -> bool:
        """Check if cloud API is accessible."""
        if not self.api_key:
            return False
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> list:
        """List available cloud models."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []

    def generate(self, prompt: str, model: str = "gpt-oss:120b", system_prompt: str = None, ai_name: str = None, ai_personality: str = None, **kwargs) -> str:
        """Generate text using Ollama Cloud API."""
        try:
            # Build system message from configuration
            system_parts = []

            if ai_name:
                system_parts.append(f"You are {ai_name}.")

            if ai_personality:
                system_parts.append(f"Your personality: {ai_personality}")

            if system_prompt:
                system_parts.append(system_prompt)

            # Combine all system instructions
            full_system = " ".join(system_parts) if system_parts else None

            messages = []
            if full_system:
                messages.append({'role': 'system', 'content': full_system})
            messages.append({'role': 'user', 'content': prompt})

            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                **kwargs
            }

            headers = {'Authorization': f'Bearer {self.api_key}'}

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                headers=headers,
                timeout=120  # Cloud models can take longer
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('message', {}).get('content', '')
            else:
                raise Exception(f"Cloud API error: {response.status_code} - {response.text}")

        except Exception as e:
            raise Exception(f"Ollama Cloud generation failed: {str(e)}")

    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            return response.status_code == 200
        except:
            return False


class WebSearchProvider:
    """Ollama Web Search API implementation."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or self._get_api_key()
        self.base_url = "https://ollama.com"

    def _get_api_key(self):
        """Get API key from keyring."""
        return keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")

    def is_available(self) -> bool:
        """Check if web search API is accessible."""
        if not self.api_key:
            return False
        try:
            # Test with a simple request to check API availability
            response = requests.post(
                f"{self.base_url}/api/web_search",
                json={"query": "test", "max_results": 1},
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )
            return response.status_code in [200, 400]  # 400 is OK for test query
        except:
            return False

    def search(self, query: str, max_results: int = 5) -> list:
        """Perform web search using Ollama's web search API."""
        try:
            payload = {
                "query": query,
                "max_results": max_results
            }

            headers = {'Authorization': f'Bearer {self.api_key}'}

            response = requests.post(
                f"{self.base_url}/api/web_search",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                raise Exception(f"Web search API error: {response.status_code} - {response.text}")

        except Exception as e:
            raise Exception(f"Web search failed: {str(e)}")


class LLMProviderManager:
    """Manages different LLM providers."""

    def __init__(self):
        self.providers = {
            'ollama': OllamaProvider(),
            'remote': None  # Will be set when EnkaliPrime client is created
        }
        self.preferred_provider = 'remote'  # Default to remote

    def set_preferred_provider(self, provider: str):
        """Set the preferred LLM provider."""
        if provider in self.providers:
            self.preferred_provider = provider

    def get_available_providers(self) -> list:
        """Get list of available providers."""
        available = []
        for name, provider in self.providers.items():
            if provider and (name == 'remote' or provider.is_available()):
                available.append(name)
        return available

    def get_client(self):
        """Get the appropriate client based on preferences and availability."""
        if self.preferred_provider == 'remote':
            return create_remote_client()
        elif self.preferred_provider in self.providers:
            provider = self.providers[self.preferred_provider]
            if provider and provider.is_available():
                return provider
            else:
                # Fallback to remote if local is not available
                console.print(f"[yellow]⚠️  {self.preferred_provider.title()} not available, falling back to remote[/yellow]")
                return create_remote_client()
        else:
            return create_remote_client()


# Global provider manager
provider_manager = LLMProviderManager()
provider_manager.providers['cloud'] = OllamaCloudProvider()

# Global web search provider
web_search_provider = WebSearchProvider()

app = typer.Typer(
    help="💬 Interactive chat with AI",
    rich_markup_mode="rich",
)


def get_api_key():
    """Get API key from keyring."""
    return keyring.get_password(SERVICE_NAME, "api_key")


def create_remote_client():
    """Create EnkaliPrime client with stored API key."""
    api_key = get_api_key()
    if not api_key:
        print_error("No API key configured.")
        console.print("Run: [cyan]enkaliprime config set-api-key[/]")
        raise typer.Exit(1)

    from enkaliprime import EnkaliPrimeClient
    client = EnkaliPrimeClient({
        "unified_api_key": api_key,
        "base_url": "https://sdk.enkaliprime.com"
    })
    provider_manager.providers['remote'] = client
    return client


def create_client():
    """Create LLM client using provider manager."""
    return provider_manager.get_client()


@app.command()
def interactive(
    agent_name: str = typer.Option(
        "CLI Assistant",
        "--agent",
        "-a",
        help="Name of the AI agent",
    ),
    provider: str = typer.Option(
        "auto",
        "--provider",
        "-p",
        help="LLM provider: auto, remote, ollama, cloud (auto detects available providers)",
    ),
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Model name for local/cloud providers (e.g., llama2, gpt-oss:120b)",
    ),
    local: bool = typer.Option(
        False,
        "--local",
        "-l",
        help="Use configured default Ollama model",
    ),
    cloud: bool = typer.Option(
        False,
        "--cloud",
        "-c",
        help="Use Ollama cloud models",
    ),
    stream: bool = typer.Option(
        False,
        "--stream",
        "-s",
        help="Enable streaming responses",
    ),
    coder: bool = typer.Option(
        False,
        "--coder",
        help="Enable coding assistant mode with project planning and file operations",
    ),
    web: bool = typer.Option(
        False,
        "--web",
        help="Enable web search augmentation for more accurate responses",
    ),
):
    """Start interactive chat session with AI."""
    try:
        console.clear()

        # Check if coder mode is enabled
        if coder:
            from ..coder import start_coder_mode
            start_coder_mode(agent_name=agent_name, provider=provider, model=model,
                           local=local, cloud=cloud)
            return

        Header.draw(agent_name=agent_name)

        # Initialize web search state (can be toggled during session)
        web_search_enabled = web

        # Handle default provider/model if no flags specified
        default_provider = keyring.get_password(SERVICE_NAME, "default_provider")
        default_model = keyring.get_password(SERVICE_NAME, "default_model")

        if not local and not cloud and default_provider:
            # Use default settings
            if default_provider == "ollama":
                if default_model:
                    provider_manager.set_preferred_provider("ollama")
                    if not model:
                        model = default_model
                    console.print(f"[dim]Using default local model: {model}[/]")
                else:
                    provider_manager.set_preferred_provider("ollama")
                    console.print("[dim]Using default local provider[/]")
            elif default_provider == "cloud":
                cloud_api_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")
                if cloud_api_key:
                    provider_manager.set_preferred_provider("cloud")
                    provider_manager.providers['cloud'] = OllamaCloudProvider(cloud_api_key)
                    if not model and default_model:
                        model = default_model
                    console.print(f"[dim]Using default cloud model: {model or 'gpt-oss:120b'}[/]")
                else:
                    console.print("[yellow]⚠️  Default cloud provider selected but API key not configured[/]")
                    provider_manager.set_preferred_provider("auto")
            elif default_provider == "remote":
                provider_manager.set_preferred_provider("remote")
                console.print("[dim]Using default remote provider[/]")
        elif cloud:
            # Check if cloud API key is configured
            cloud_api_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")
            if not cloud_api_key:
                console.print("[yellow]⚠️  Ollama cloud API key not configured.[/]")
                console.print("Set one with: [cyan]enkaliprime config set-ollama-cloud-key[/]")
                console.print("Falling back to auto provider...")
                provider_manager.set_preferred_provider("auto")
            else:
                provider_manager.set_preferred_provider("cloud")
                provider_manager.providers['cloud'] = OllamaCloudProvider(cloud_api_key)
                if not model:  # Use default cloud model if set, otherwise gpt-oss:120b
                    default_cloud_model = keyring.get_password(SERVICE_NAME, "default_cloud_model")
                    model = default_cloud_model if default_cloud_model else "gpt-oss:120b"
        elif local:
            default_model = keyring.get_password(SERVICE_NAME, "ollama_model")
            if default_model:
                provider_manager.set_preferred_provider("ollama")
                if not model:  # Don't override if user specified a specific model
                    model = default_model
            else:
                console.print("[yellow]⚠️  No default Ollama model configured.[/]")
                console.print("Set one with: [cyan]enkaliprime config set-ollama-model[/]")
                console.print("Falling back to remote provider...")
        elif provider != "auto":
            provider_manager.set_preferred_provider(provider)

        available_providers = provider_manager.get_available_providers()
        current_provider = provider_manager.preferred_provider

        # Show provider information
        if current_provider == "remote":
            console.print(f"\n[dim]🤖 Using remote AI provider (EnkaliPrime)[/]")
        else:
            console.print(f"\n[dim]🏠 Using local AI provider ({current_provider})[/]")
            if model:
                console.print(f"[dim]📋 Model: {model}[/]")

        # Show web search status
        web_status = "Active" if web_search_enabled else "Inactive"
        web_color = COLOR_ACCENT if web_search_enabled else COLOR_DIM
        console.print(f"[dim]🌐 Web Search: [{web_color}]{web_status}[/][/]")

        console.print(f"\n[dim]Type 'exit', 'quit', or 'q' to end the conversation.[/]")
        console.print(f"[dim]Type '/' for available commands.[/]")
        console.print()

        # Create client and session
        client = create_client()

        # For remote provider, create session; for local, no session needed
        if hasattr(client, 'create_session'):
            session = client.create_session(agent_name=agent_name)
            session_id = session.id if session else None
            print_success(f"Session started: {session_id}")
        else:
            session_id = None
            if model:
                print_success(f"Connected to local LLM: {model}")
            else:
                print_success("Connected to local LLM")

        console.print()

        while True:
            # Get user input
            try:
                user_input = Prompt.ask(f"[bold {COLOR_ACCENT}]You[/]").strip()
            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Goodbye![/]")
                break

            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]👋 Goodbye![/]")
                break

            if not user_input:
                continue

            # Handle slash commands
            if user_input.startswith('/'):
                command = user_input[1:].strip().lower()
                if command == '':
                    # Show available commands
                    console.print()
                    console.print(cyber_panel(
                        "[bold cyan]/web[/] - Toggle web search on/off\n"
                        "[bold cyan]/status[/] - Show current settings\n"
                        "[bold cyan]/help[/] - Show this help",
                        title="Available Commands",
                        style=COLOR_SECONDARY
                    ))
                    console.print()
                    continue
                elif command == 'web':
                    # Toggle web search
                    web_search_enabled = not web_search_enabled
                    status = "enabled" if web_search_enabled else "disabled"
                    color = COLOR_ACCENT if web_search_enabled else "red"
                    console.print(f"[bold {color}]🌐 Web search {status}[/]")

                    # Update status display
                    web_status = "Active" if web_search_enabled else "Inactive"
                    web_color = COLOR_ACCENT if web_search_enabled else COLOR_DIM
                    console.print(f"[dim]🌐 Web Search: [{web_color}]{web_status}[/][/]")
                    console.print()
                    continue
                elif command == 'status':
                    # Show current status
                    web_status = "Active" if web_search_enabled else "Inactive"
                    web_color = COLOR_ACCENT if web_search_enabled else COLOR_DIM
                    console.print(cyber_panel(
                        f"🤖 Provider: {current_provider}\n"
                        f"🌐 Web Search: [{web_color}]{web_status}[/]",
                        title="Current Status",
                        style=COLOR_SECONDARY
                    ))
                    console.print()
                    continue
                elif command == 'help':
                    # Show help (same as empty /)
                    console.print()
                    console.print(cyber_panel(
                        "[bold cyan]/web[/] - Toggle web search on/off\n"
                        "[bold cyan]/status[/] - Show current settings\n"
                        "[bold cyan]/help[/] - Show this help",
                        title="Available Commands",
                        style=COLOR_SECONDARY
                    ))
                    console.print()
                    continue
                else:
                    console.print(f"[yellow]Unknown command: /{command}[/]")
                    console.print("[dim]Type '/' for available commands.[/]")
                    console.print()
                    continue

            try:
                # Prepare the message, potentially with web search augmentation
                final_message = user_input

                # Web search augmentation
                if web_search_enabled:
                    if web_search_provider.is_available():
                        console.print(f"[dim]🔍 Searching web for: {user_input[:50]}{'...' if len(user_input) > 50 else ''}[/]")
                        try:
                            search_results = web_search_provider.search(user_input, max_results=3)
                            if search_results:
                                # Format search results for AI context
                                web_context = "\n\nWeb Search Results:\n"
                                for i, result in enumerate(search_results, 1):
                                    web_context += f"{i}. **{result['title']}**\n   {result['content']}\n   Source: {result['url']}\n\n"

                                final_message = f"{user_input}\n\n{web_context.strip()}"
                                console.print(f"[dim]📚 Found {len(search_results)} relevant results[/]")
                            else:
                                console.print("[dim yellow]⚠️ No web search results found[/]")
                        except Exception as e:
                            console.print(f"[dim yellow]⚠️ Web search failed: {str(e)}[/]")
                    else:
                        console.print("[dim yellow]⚠️ Web search not available (check Ollama Cloud API key)[/]")

                # Send message based on provider type
                if hasattr(client, 'send_message'):
                    # Remote provider (EnkaliPrime)
                    response = client.send_message(
                        message=final_message,
                        session_id=session_id,
                        loading=False,  # Disable CLI loading to avoid PowerShell conflicts
                    )
                else:
                    # Local provider - get behavior settings
                    model_name = model or "llama2"  # Default model

                    # Get behavior configuration
                    system_prompt = keyring.get_password(SERVICE_NAME, "system_prompt")
                    ai_name = keyring.get_password(SERVICE_NAME, "ai_name")
                    ai_personality = keyring.get_password(SERVICE_NAME, "ai_personality")

                    response = client.generate(
                        final_message,
                        model=model_name,
                        system_prompt=system_prompt,
                        ai_name=ai_name,
                        ai_personality=ai_personality
                    )

            except Exception as e:
                print_error(f"Error: {str(e)}")
                continue

            # Process response for code blocks and display
            processed_response = process_ai_response(response, interactive=True)
            console.print(cyber_panel(
                Markdown(processed_response),
                title=agent_name,
                style=COLOR_SECONDARY
            ))
            console.print()

    except Exception as e:
        print_error(f"Chat session failed: {str(e)}")
        raise typer.Exit(1)


@app.command()
def ask(
    message: str = typer.Argument(..., help="Message to send to AI"),
    agent_name: str = typer.Option(
        "CLI Assistant",
        "--agent",
        "-a",
        help="Name of the AI agent",
    ),
    provider: str = typer.Option(
        "auto",
        "--provider",
        "-p",
        help="LLM provider: auto, remote, ollama, cloud (auto detects available providers)",
    ),
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Model name for local/cloud providers (e.g., llama2, gpt-oss:120b)",
    ),
    local: bool = typer.Option(
        False,
        "--local",
        "-l",
        help="Use configured default Ollama model",
    ),
    cloud: bool = typer.Option(
        False,
        "--cloud",
        "-c",
        help="Use Ollama cloud models",
    ),
    web: bool = typer.Option(
        False,
        "--web",
        help="Enable web search augmentation for more accurate responses",
    ),
):
    """Send a single message to AI and get response."""
    try:
        # Handle default provider/model if no flags specified
        default_provider = keyring.get_password(SERVICE_NAME, "default_provider")
        default_model = keyring.get_password(SERVICE_NAME, "default_model")

        if not local and not cloud and default_provider:
            # Use default settings
            if default_provider == "ollama":
                if default_model:
                    provider_manager.set_preferred_provider("ollama")
                    if not model:
                        model = default_model
            elif default_provider == "cloud":
                cloud_api_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")
                if cloud_api_key:
                    provider_manager.set_preferred_provider("cloud")
                    provider_manager.providers['cloud'] = OllamaCloudProvider(cloud_api_key)
                    if not model and default_model:
                        model = default_model
                else:
                    provider_manager.set_preferred_provider("auto")
            elif default_provider == "remote":
                provider_manager.set_preferred_provider("remote")
        elif cloud:
            # Check if cloud API key is configured
            cloud_api_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")
            if not cloud_api_key:
                console.print("[yellow]⚠️  Ollama cloud API key not configured.[/]")
                console.print("Set one with: [cyan]enkaliprime config set-ollama-cloud-key[/]")
                console.print("Falling back to auto provider...")
                provider_manager.set_preferred_provider("auto")
            else:
                provider_manager.set_preferred_provider("cloud")
                provider_manager.providers['cloud'] = OllamaCloudProvider(cloud_api_key)
                if not model:  # Use default cloud model if set, otherwise gpt-oss:120b
                    default_cloud_model = keyring.get_password(SERVICE_NAME, "default_cloud_model")
                    model = default_cloud_model if default_cloud_model else "gpt-oss:120b"
        elif local:
            default_model = keyring.get_password(SERVICE_NAME, "ollama_model")
            if default_model:
                provider_manager.set_preferred_provider("ollama")
                if not model:  # Don't override if user specified a specific model
                    model = default_model
            else:
                console.print("[yellow]⚠️  No default Ollama model configured.[/]")
                console.print("Set one with: [cyan]enkaliprime config set-ollama-model[/]")
                console.print("Falling back to remote provider...")
        elif provider != "auto":
            provider_manager.set_preferred_provider(provider)

        client = create_client()

        try:
            # Prepare the message, potentially with web search augmentation
            final_message = message

            # Web search augmentation
            if web:
                if web_search_provider.is_available():
                    console.print(f"[dim]🔍 Searching web for: {message[:50]}{'...' if len(message) > 50 else ''}[/]")
                    try:
                        search_results = web_search_provider.search(message, max_results=3)
                        if search_results:
                            # Format search results for AI context
                            web_context = "\n\nWeb Search Results:\n"
                            for i, result in enumerate(search_results, 1):
                                web_context += f"{i}. **{result['title']}**\n   {result['content']}\n   Source: {result['url']}\n\n"

                            final_message = f"{message}\n\n{web_context.strip()}"
                            console.print(f"[dim]📚 Found {len(search_results)} relevant results[/]")
                        else:
                            console.print("[dim yellow]⚠️ No web search results found[/]")
                    except Exception as e:
                        console.print(f"[dim yellow]⚠️ Web search failed: {str(e)}[/]")
                else:
                    console.print("[dim yellow]⚠️ Web search not available (check Ollama Cloud API key)[/]")

            # Send message based on provider type
            if hasattr(client, 'send_message'):
                # Remote provider (EnkaliPrime)
                session = client.create_session(agent_name=agent_name)
                response = client.send_message(
                    message=final_message,
                    session_id=session.id,
                    loading=False,  # Disable CLI loading to avoid PowerShell conflicts
                )
            else:
                # Local provider - get behavior settings
                model_name = model or "llama2"  # Default model

                # Get behavior configuration
                system_prompt = keyring.get_password(SERVICE_NAME, "system_prompt")
                ai_name = keyring.get_password(SERVICE_NAME, "ai_name")
                ai_personality = keyring.get_password(SERVICE_NAME, "ai_personality")

                response = client.generate(
                    final_message,
                    model=model_name,
                    system_prompt=system_prompt,
                    ai_name=ai_name,
                    ai_personality=ai_personality
                )

        except Exception as e:
            print_error("Request failed")
            raise

        # Process response for code blocks and display
        processed_response = process_ai_response(response, interactive=False)
        console.print(cyber_panel(
            Markdown(processed_response),
            title=agent_name,
            style=COLOR_SECONDARY
        ))

    except Exception as e:
        print_error(f"Failed to get response: {str(e)}")
        raise typer.Exit(1)


@app.command()
def copy(
    index: int = typer.Option(0, "--index", "-i", help="Code block index (0-based, default: 0)"),
    all_blocks: bool = typer.Option(False, "--all", "-a", help="Copy all code blocks"),
    show_blocks: bool = typer.Option(False, "--show", "-s", help="Show all code blocks"),
):
    """Copy code blocks from the last AI response to clipboard."""
    try:
        if show_blocks:
            show_code_blocks()
            return

        if all_blocks:
            if copy_all_code():
                console.print("[green]✅ All code blocks copied to clipboard![/]")
            else:
                console.print("[red]❌ No code blocks found in the last response[/red]")
        else:
            if copy_code_block(index):
                console.print(f"[green]✅ Code block #{index} copied to clipboard![/]")
            else:
                console.print(f"[red]❌ Code block #{index} not found. Use --show to see available blocks.[/red]")

    except Exception as e:
        console.print(f"[red]❌ Failed to copy code: {str(e)}[/red]")


@app.command()
def providers():
    """List available LLM providers and models."""
    try:
        available_providers = provider_manager.get_available_providers()

        table = Table(title="🤖 Available LLM Providers", box=box.ROUNDED)
        table.add_column("Provider", style=f"bold {COLOR_PRIMARY}")
        table.add_column("Status", style="bold")
        table.add_column("Models", style="dim")

        # Check remote provider
        remote_available = "remote" in available_providers
        table.add_row(
            "EnkaliPrime (Remote)",
            f"[{'green' if remote_available else 'red'}]{'✓ Available' if remote_available else '✗ Needs API Key'}[/]",
            "Various models via API"
        )

        # Check local providers
        for provider_name in ['ollama']:
            if provider_name in provider_manager.providers:
                provider = provider_manager.providers[provider_name]
                is_available = provider.is_available()
                models = provider.list_models() if is_available else []
                model_list = ", ".join(models[:5]) + ("..." if len(models) > 5 else "") if models else "None"

                table.add_row(
                    f"{provider_name.title()} (Local)",
                    f"[{'green' if is_available else 'red'}]{'✓ Running' if is_available else '✗ Not running'}[/]",
                    model_list or "Not available"
                )

        # Check cloud provider
        if 'cloud' in provider_manager.providers:
            provider = provider_manager.providers['cloud']
            is_available = provider.is_available()
            models = provider.list_models() if is_available else []
            model_list = ", ".join(models[:5]) + ("..." if len(models) > 5 else "") if models else "None"

            table.add_row(
                "Ollama Cloud",
                f"[{'green' if is_available else 'red'}]{'✓ Available' if is_available else '✗ Needs API Key'}[/]",
                model_list or "Not available"
            )

        console.print(table)

        # Show instructions
        console.print(f"\n[bold {COLOR_ACCENT}]💡 Usage:[/]")
        console.print(f"• [cyan]enkaliprime chat interactive --provider ollama --model llama2[/]")
        console.print(f"• [cyan]enkaliprime chat interactive --cloud --model gpt-oss:120b[/]")
        console.print(f"• [cyan]enkaliprime chat interactive --web[/] (with web search)")
        console.print(f"• [cyan]enkaliprime chat ask \"Hello\" --provider remote[/]")
        console.print(f"• [cyan]enkaliprime chat providers[/] (this command)")

        if not any(p in available_providers for p in ['ollama']):
            console.print(f"\n[yellow]💡 To use local LLMs:[/]")
            console.print(f"• Install Ollama: [cyan]https://ollama.ai/[/]")
            console.print(f"• Pull a model: [cyan]ollama pull llama2[/]")
            console.print(f"• Start Ollama: [cyan]ollama serve[/]")

        if 'cloud' not in available_providers:
            console.print(f"\n[yellow]💡 To use cloud LLMs:[/]")
            console.print(f"• Get API key: [cyan]https://ollama.com/settings/keys[/]")
            console.print(f"• Set API key: [cyan]enkaliprime config set-ollama-cloud-key[/]")

        console.print(f"\n[yellow]💡 Interactive commands:[/]")
        console.print(f"• During chat, type [cyan]/[/] to see available commands")
        console.print(f"• Use [cyan]/web[/] to toggle web search on/off")
        console.print(f"• Use [cyan]/status[/] to check current settings")

    except Exception as e:
        print_error(f"Failed to check providers: {str(e)}")
        raise typer.Exit(1)


@app.command()
def history():
    """Show conversation history for current session."""
    try:
        client = create_client()

        if not client.current_session:
            print_error("No active session.")
            console.print("Start a chat with: [cyan]enkaliprime chat interactive[/]")
            return

        history = client.get_history()

        if not history:
            console.print("[yellow]📝 No conversation history yet.[/]")
            return
        
        Header.draw("History Viewer")
        console.print(f"\n[bold {COLOR_PRIMARY}]Conversation History ({len(history)//2} exchanges)[/]")
        console.print()

        table = Table(box=box.ROUNDED, border_style=COLOR_DIM)
        table.add_column("Role", style=f"bold {COLOR_PRIMARY}", width=10)
        table.add_column("Message", style="white")

        for message in history:
            role = message["role"]
            content = message["content"]
            
            # Truncate content for table view if too long, or keep it basic
            display_role = "You" if role == "user" else "AI"
            role_style = COLOR_ACCENT if role == "user" else COLOR_SECONDARY
            
            table.add_row(
                f"[{role_style}]{display_role}[/]",
                content
            )

        console.print(table)
        console.print()

    except Exception as e:
        print_error(f"Failed to get history: {str(e)}")
        raise typer.Exit(1)

