"""
Code block processing utilities for EnkaliPrime CLI.
Provides copy-to-clipboard functionality for code blocks in AI responses.
"""

import re
import pyperclip
from typing import List, Tuple, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.columns import Columns
from rich.align import Align

console = Console()


class CodeBlockProcessor:
    """Processes code blocks in AI responses and provides copy functionality."""

    def __init__(self):
        self.last_code_blocks = []

    def extract_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        """Extract code blocks from markdown text.

        Returns:
            List of tuples (language, code) for each code block found.
        """
        # Regex to match markdown code blocks: ```language\ncode\n```
        code_block_pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.findall(code_block_pattern, text, re.DOTALL)

        # Also match inline code blocks without language
        inline_pattern = r'```(.*?)```'
        inline_matches = re.findall(inline_pattern, text, re.DOTALL)

        # Filter out inline matches that are already in the main matches
        code_blocks = []
        for match in matches:
            lang, code = match
            lang = lang.strip() if lang.strip() else "text"
            code = code.strip()
            if code:  # Only add non-empty code blocks
                code_blocks.append((lang, code))

        # Add inline code blocks that aren't part of larger blocks
        for inline_code in inline_matches:
            inline_code = inline_code.strip()
            if inline_code and len(inline_code.split('\n')) > 1:  # Multi-line inline code
                # Check if this inline code is already captured
                if not any(inline_code in existing_code for _, existing_code in code_blocks):
                    code_blocks.append(("text", inline_code))

        return code_blocks

    def process_response(self, response_text: str, show_copy_options: bool = True) -> str:
        """Process AI response and add copy functionality for code blocks.

        Args:
            response_text: The AI response text
            show_copy_options: Whether to show interactive copy options

        Returns:
            Processed response text with copy indicators
        """
        self.last_code_blocks = self.extract_code_blocks(response_text)

        if not self.last_code_blocks:
            return response_text

        # Add copy indicators to the response
        processed_text = response_text

        # Replace code blocks with enhanced versions
        for i, (lang, code) in enumerate(self.last_code_blocks, 1):
            # Create a copy indicator
            copy_indicator = f"\n\n[dim cyan]┌─ Code Block #{i} ({lang}) ─[/dim cyan]\n[dim cyan]│ 📋 Press 'c' to copy to clipboard[/dim cyan]\n[dim cyan]└─────────────────────────────────────[/dim cyan]"

            # Add the indicator after each code block
            code_block_pattern = f'```{lang}\n{re.escape(code)}\n```'
            processed_text = re.sub(
                code_block_pattern,
                f'```{lang}\n{code}\n```{copy_indicator}',
                processed_text,
                count=1
            )

        # Show interactive copy options if requested
        if show_copy_options and self.last_code_blocks:
            console.print()  # Add some space
            self.show_copy_menu()

        return processed_text

    def show_copy_menu(self):
        """Show an interactive menu for copying code blocks."""
        if not self.last_code_blocks:
            return

        console.print("[bold cyan]📋 Code Copy Options:[/]")
        console.print("[dim]The response contains code blocks you can copy:[/]")

        for i, (lang, code) in enumerate(self.last_code_blocks, 1):
            # Show a preview of the code (first line or truncated)
            preview = code.split('\n')[0][:50]
            if len(code.split('\n')) > 1 or len(code) > 50:
                preview += "..."

            console.print(f"[cyan]{i}.[/cyan] [bold]{lang}[/] - [dim]{preview}[/]")

        console.print()
        console.print("[dim]Choose an option:[/]")
        console.print("[dim]• Enter a number (1-{}) to copy that code block[/dim]".format(len(self.last_code_blocks)))
        console.print("[dim]• Press 'a' to copy all code blocks[/dim]")
        console.print("[dim]• Press Enter to continue[/dim]")

        try:
            choice = Prompt.ask("", default="", show_default=False).strip().lower()

            if choice == 'a':
                # Copy all code blocks concatenated
                all_code = "\n\n".join([f"# {lang.upper()}\n{code}" for lang, code in self.last_code_blocks])
                self.copy_to_clipboard(all_code)
                console.print("[green]✅ All code blocks copied to clipboard![/]")

            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(self.last_code_blocks):
                    lang, code = self.last_code_blocks[idx]
                    self.copy_to_clipboard(code)
                    console.print(f"[green]✅ Code block #{idx + 1} ({lang}) copied to clipboard![/]")
                else:
                    console.print("[red]❌ Invalid selection[/red]")

        except (EOFError, KeyboardInterrupt):
            # User pressed Ctrl+C or similar, just continue
            pass

    def copy_last_code_block(self, index: int = 0) -> bool:
        """Copy a specific code block to clipboard.

        Args:
            index: Index of the code block (0-based)

        Returns:
            True if successful, False otherwise
        """
        if 0 <= index < len(self.last_code_blocks):
            _, code = self.last_code_blocks[index]
            return self.copy_to_clipboard(code)
        return False

    def copy_all_code_blocks(self) -> bool:
        """Copy all code blocks to clipboard.

        Returns:
            True if successful, False otherwise
        """
        if self.last_code_blocks:
            all_code = "\n\n".join([f"# {lang.upper()}\n{code}" for lang, code in self.last_code_blocks])
            return self.copy_to_clipboard(all_code)
        return False

    def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to system clipboard.

        Args:
            text: Text to copy

        Returns:
            True if successful, False otherwise
        """
        try:
            pyperclip.copy(text)
            return True
        except Exception as e:
            console.print(f"[red]❌ Failed to copy to clipboard: {str(e)}[/red]")
            console.print("[yellow]💡 Make sure you have the proper clipboard tools installed[/yellow]")
            return False

    def get_code_block_count(self) -> int:
        """Get the number of code blocks in the last processed response."""
        return len(self.last_code_blocks)

    def show_code_blocks(self):
        """Display all code blocks with syntax highlighting."""
        if not self.last_code_blocks:
            console.print("[yellow]No code blocks found in the last response.[/]")
            return

        for i, (lang, code) in enumerate(self.last_code_blocks, 1):
            console.print(f"\n[bold cyan]Code Block #{i} - {lang.upper()}[/]")

            # Create a panel with the code
            from rich.syntax import Syntax
            syntax = Syntax(code, lang if lang != "text" else None, theme="monokai", line_numbers=True)

            panel = Panel(
                Align.center(syntax),
                title=f"[bold]{lang}[/bold]",
                border_style="blue",
                title_align="left"
            )
            console.print(panel)


# Global instance
code_processor = CodeBlockProcessor()


def process_ai_response(response_text: str, interactive: bool = True) -> str:
    """Process an AI response and add copy functionality.

    Args:
        response_text: The AI response text
        interactive: Whether to show interactive copy menu

    Returns:
        Processed response text
    """
    return code_processor.process_response(response_text, interactive)


def copy_code_block(index: int = 0) -> bool:
    """Copy a specific code block to clipboard.

    Args:
        index: Code block index (0-based)

    Returns:
        True if successful
    """
    return code_processor.copy_last_code_block(index)


def copy_all_code() -> bool:
    """Copy all code blocks to clipboard.

    Returns:
        True if successful
    """
    return code_processor.copy_all_code_blocks()


def show_code_blocks():
    """Display all code blocks with syntax highlighting."""
    code_processor.show_code_blocks()
