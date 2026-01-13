"""
Modern chat interface for EnkaliPrime CLI.

Provides a conversational interface similar to Gemini CLI.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich import box
from rich.align import Align
from typing import Optional
import re

console = Console()


class ModernChatInterface:
    """Modern conversational interface for command selection."""

    def __init__(self):
        self.command_patterns = {
            # Chat commands
            r'\b(chat|talk|converse|interactive)\b': ["enkaliprime", "chat", "interactive"],
            r'\b(ask|question|query)\b': ["enkaliprime", "chat", "ask"],
            r'\b(code|coder|develop|programming)\b': ["enkaliprime", "chat", "interactive", "--coder"],

            # Configuration commands
            r'\b(config|configure|settings|setup|api)\b': ["enkaliprime", "config", "show"],

            # Session commands
            r'\b(session|sessions|history)\b': ["enkaliprime", "session", "current"],

            # Info commands
            r'\b(info|information|about|help)\b': ["enkaliprime", "info"],

            # Help commands
            r'\b(help|commands|usage)\b': ["enkaliprime", "--help"],

            # Exit commands
            r'\b(exit|quit|bye|goodbye|leave)\b': None,
        }

    def display_welcome(self) -> Panel:
        """Create and display the modern welcome interface."""
        welcome_text = Text()
        welcome_text.append("Welcome to ", style="bold cyan")
        welcome_text.append("EnkaliPrime CLI", style="bold white")
        welcome_text.append("\n\nA modern AI chat interface for your terminal\n\n", style="dim")

        # Quick commands hint
        welcome_text.append("* Quick commands:\n", style="yellow")
        welcome_text.append("• 'chat' or 'talk' - Start interactive chat\n", style="dim white")
        welcome_text.append("• 'code' or 'coder' - Start coding assistant mode\n", style="dim white")
        welcome_text.append("• 'ask' or 'question' - Quick question & answer\n", style="dim white")
        welcome_text.append("• 'config' or 'settings' - Manage configuration\n", style="dim white")
        welcome_text.append("• 'session' or 'history' - View chat sessions\n", style="dim white")
        welcome_text.append("• 'info' or 'about' - Show CLI information\n", style="dim white")
        welcome_text.append("• 'help' - Show help & commands\n", style="dim white")
        welcome_text.append("• 'exit' or 'quit' - Exit the CLI\n\n", style="dim white")

        # Local LLM hint
        welcome_text.append("* Local AI (Ollama):\n", style="cyan")
        welcome_text.append("• Configure: 'enkaliprime config set-ollama-model'\n", style="dim cyan")
        welcome_text.append("• Customize: 'enkaliprime config set-system-prompt'\n", style="dim cyan")
        welcome_text.append("• Use local: Add --local flag to chat commands\n", style="dim cyan")
        welcome_text.append("• Check status: 'enkaliprime config show-behavior'\n\n", style="dim cyan")

        # Global default hint
        welcome_text.append("* Global Default AI:\n", style="green")
        welcome_text.append("• Set once: 'enkaliprime config set-default-model'\n", style="dim green")
        welcome_text.append("• Use everywhere: Just run chat commands\n", style="dim green")
        welcome_text.append("• No flags needed: Works automatically\n\n", style="dim green")

        # Cloud LLM hint
        welcome_text.append("* Cloud AI (Ollama Cloud):\n", style="magenta")
        welcome_text.append("• Setup: 'enkaliprime config set-ollama-cloud-key'\n", style="dim magenta")
        welcome_text.append("• Set default: 'enkaliprime config set-default-cloud-model'\n", style="dim magenta")
        welcome_text.append("• Use cloud: Add --cloud flag to chat commands\n", style="dim magenta")
        welcome_text.append("• View models: 'enkaliprime config show-cloud'\n\n", style="dim magenta")

        # Create a sleek panel
        welcome_panel = Panel(
            Align.left(welcome_text),
            title="[bold cyan]EnkaliPrime CLI[/bold cyan]",
            title_align="left",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 3)
        )

        return welcome_panel

    def parse_command(self, user_input: str) -> Optional[list]:
        """Parse natural language input to determine the intended command."""
        user_input = user_input.lower().strip()

        # Direct command mapping for common phrases
        for pattern, command in self.command_patterns.items():
            if re.search(pattern, user_input):
                return command

        # If no pattern matches, try to interpret as a chat request
        if user_input and len(user_input) > 0:
            # If it looks like a question or statement, default to chat
            if user_input.endswith('?') or len(user_input.split()) > 2:
                return ["enkaliprime", "chat", "ask"]
            else:
                return ["enkaliprime", "chat", "interactive"]

        return None

    def get_user_input(self) -> Optional[str]:
        """Get user input with modern chat prompt."""
        try:
            # Create a modern chat prompt
            prompt_text = Text(">", style="bold blue")
            prompt_text.append(" Ask me anything", style="bold cyan")
            prompt_text.append(" (or type 'help' for commands)", style="dim white")

            user_input = Prompt.ask(prompt_text, default="")
            return user_input.strip()
        except (KeyboardInterrupt, EOFError):
            return "exit"  # Exit on Ctrl+C
        except Exception:
            return None

    def get_command_info(self, command: list) -> dict:
        """Get detailed information about a command."""
        cmd_str = ' '.join(command)

        command_docs = {
            'enkaliprime chat interactive': {
                'title': '🤖 Interactive Chat Mode',
                'description': 'Start a real-time conversational session with the AI',
                'features': [
                    '• Continuous back-and-forth conversation',
                    '• Maintains conversation context',
                    '• Rich text formatting and markdown support',
                    '• Session persistence across messages'
                ],
                'usage': 'enkaliprime chat interactive',
                'example': 'enkaliprime chat interactive --agent "Code Assistant"'
            },
            'enkaliprime chat ask': {
                'title': '❓ Quick Question & Answer',
                'description': 'Ask a single question and get an immediate response',
                'features': [
                    '• Perfect for quick queries',
                    '• No session overhead',
                    '• Fast response times',
                    '• Ideal for one-off questions'
                ],
                'usage': 'enkaliprime chat ask "Your question here"',
                'example': 'enkaliprime chat ask "What is the capital of France?"'
            },
            'enkaliprime chat copy': {
                'title': '📋 Copy Code Blocks',
                'description': 'Copy code blocks from AI responses to your clipboard',
                'features': [
                    '• Copy specific code blocks by index',
                    '• Copy all code blocks at once',
                    '• View code blocks with syntax highlighting',
                    '• Works with any previous AI response'
                ],
                'usage': 'enkaliprime chat copy --index 0',
                'example': 'enkaliprime chat copy --all'
            },
            'enkaliprime chat interactive --coder': {
                'title': '🎨 Coding Assistant Mode',
                'description': 'Advanced coding assistant with project planning, file operations, and implementation tracking',
                'features': [
                    '• Create detailed implementation plans',
                    '• Generate and manage project files',
                    '• Interactive progress tracking',
                    '• Safe file system operations',
                    '• AI-powered code generation'
                ],
                'usage': 'enkaliprime chat interactive --coder',
                'example': 'enkaliprime chat interactive --coder --model llama2'
            },
            'enkaliprime config show': {
                'title': '⚙️ Configuration Management',
                'description': 'View and manage your CLI configuration settings',
                'features': [
                    '• Display current API key status',
                    '• View all configuration options',
                    '• Check system information',
                    '• Secure keyring integration'
                ],
                'usage': 'enkaliprime config show',
                'example': 'enkaliprime config set-api-key'
            },
            'enkaliprime session current': {
                'title': '📝 Session Management',
                'description': 'View information about your current chat session',
                'features': [
                    '• Display active session details',
                    '• View session history',
                    '• Check session status',
                    '• Manage multiple conversations'
                ],
                'usage': 'enkaliprime session current',
                'example': 'enkaliprime session history'
            },
            'enkaliprime info': {
                'title': 'ℹ️ CLI Information',
                'description': 'Display detailed information about the EnkaliPrime CLI',
                'features': [
                    '• Version information',
                    '• Available commands overview',
                    '• System requirements',
                    '• Getting started guide'
                ],
                'usage': 'enkaliprime info',
                'example': 'enkaliprime --help'
            },
            'enkaliprime config show-ollama': {
                'title': '🏠 Ollama Configuration',
                'description': 'View Ollama status and configure local LLM settings',
                'features': [
                    '• Check Ollama connection',
                    '• List available models',
                    '• Set default model for --local flag',
                    '• Monitor model sizes and status'
                ],
                'usage': 'enkaliprime config show-ollama',
                'example': 'enkaliprime config set-ollama-model'
            },
            'enkaliprime config set-system-prompt': {
                'title': '📝 AI Behavior Configuration',
                'description': 'Customize how your local AI behaves and responds',
                'features': [
                    '• Set custom system prompts',
                    '• Define AI personality traits',
                    '• Give your AI a custom name',
                    '• Control response style and behavior',
                    '• Reset to default behavior'
                ],
                'usage': 'enkaliprime config set-system-prompt',
                'example': 'enkaliprime config reset-ai-behavior'
            },
            'enkaliprime config set-ollama-cloud-key': {
                'title': '☁️ Ollama Cloud Configuration',
                'description': 'Configure access to powerful cloud models',
                'features': [
                    '• Set API key for ollama.com',
                    '• Set default cloud model',
                    '• Access large models like GPT-OSS',
                    '• No local GPU requirements',
                    '• Test connection and view models'
                ],
                'usage': 'enkaliprime config set-ollama-cloud-key',
                'example': 'enkaliprime config set-default-cloud-model'
            },
            'enkaliprime config set-default-model': {
                'title': '🎯 Global Default Model',
                'description': 'Set your primary AI model from all available providers',
                'features': [
                    '• Choose from all local & cloud models',
                    '• Set one default for all chat commands',
                    '• No need to specify --local or --cloud',
                    '• Easy switching between providers',
                    '• Intelligent provider selection'
                ],
                'usage': 'enkaliprime config set-default-model',
                'example': 'enkaliprime chat interactive  # Uses your default'
            }
        }

        return command_docs.get(cmd_str, {
            'title': f'🔧 Command: {cmd_str}',
            'description': f'Execute the {cmd_str} command',
            'features': ['• Direct command execution', '• Full CLI functionality'],
            'usage': cmd_str,
            'example': cmd_str
        })

    def execute_command(self, command: list) -> bool:
        """Show detailed information about the parsed command."""
        if command is None:
            console.print("\n[green]Goodbye! Thanks for using EnkaliPrime CLI![/green]")
            return False

        cmd_info = self.get_command_info(command)

        # Display command information in a styled panel
        console.print()
        console.print(Panel.fit(
            f"[bold cyan]{cmd_info['title']}[/bold cyan]\n\n"
            f"[white]{cmd_info['description']}[/white]\n\n"
            f"[bold yellow]✨ Features:[/bold yellow]\n" +
            '\n'.join(cmd_info['features']) + '\n\n'
            f"[bold green]📖 Usage:[/bold green]\n"
            f"[dim]{cmd_info['usage']}[/dim]\n\n"
            f"[bold blue]💡 Example:[/bold blue]\n"
            f"[dim]{cmd_info['example']}[/dim]",
            title="[bold magenta]Command Information[/bold magenta]",
            border_style="cyan",
            padding=(1, 2)
        ))
        console.print()

        return True

    def run(self):
        """Run the modern chat interface loop."""
        console.print(self.display_welcome())

        while True:
            user_input = self.get_user_input()

            if user_input is None:
                console.print("[red]❌ Error reading input. Please try again.[/red]")
                continue

            if not user_input:  # Empty input
                console.print("[dim]Please enter a command or question...[/dim]")
                continue

            command = self.parse_command(user_input)

            if command is None:
                console.print("[yellow]I didn't understand that command. Try 'help' for available options.[/yellow]")
                continue

            if not self.execute_command(command):
                break

            console.clear()
            # Show welcome again for next interaction
            console.print(self.display_welcome())


def show_interactive_menu():
    """Show the modern chat interface."""
    chat_interface = ModernChatInterface()
    chat_interface.run()
