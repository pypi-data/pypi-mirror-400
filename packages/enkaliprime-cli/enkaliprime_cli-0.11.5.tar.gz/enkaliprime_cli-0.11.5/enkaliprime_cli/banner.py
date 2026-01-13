"""
Startup banner for EnkaliPrime CLI.

Displays custom ASCII art and branding on startup, similar to Gemini's design.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()


class StartupBanner:
    """Handles the display of the custom startup banner."""

    def __init__(self, config_path: str = None):
        """Initialize the banner with configuration.

        Args:
            config_path: Path to config.jsonc file. If None, uses default location.
        """
        if config_path is None:
            # Try to find config.jsonc in the package
            package_dir = Path(__file__).parent
            config_path = package_dir / "config.jsonc"

            # If not found in package, try the project root
            if not config_path.exists():
                config_path = package_dir.parent / "config.jsonc"

        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load and parse the configuration file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                # Remove comments for JSON parsing (basic implementation)
                content = f.read()
                # Remove // comments
                lines = []
                for line in content.split('\n'):
                    # Remove everything after //
                    if '//' in line:
                        line = line.split('//')[0]
                    lines.append(line)
                content = '\n'.join(lines)

                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            console.print(f"[red]Warning: Could not load banner config: {e}[/]")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return a minimal default configuration."""
        return {
            "branding": {
                "name": "ENKALIPRIME CLI",
                "version": "1.0.0"
            },
            "colors": {
                "$1": "cyan",
                "$2": "green",
                "$3": "magenta"
            },
            "asciiArt": [
                "╔══════════════════════╗",
                "║   ENKALIPRIME CLI    ║",
                "╚══════════════════════╝"
            ],
            "sideText": [
                {"color": "$1", "text": "Welcome to EnkaliPrime"}
            ],
            "layout": {
                "gap": 4,
                "centerVertically": True
            },
            "boot": {
                "showBanner": True,
                "animate": False
            }
        }

    def _resolve_color(self, color_code: str) -> str:
        """Resolve color code ($1-$9) to actual color name."""
        if color_code in self.config.get("colors", {}):
            return self.config["colors"][color_code]
        return "white"  # fallback

    def _create_art_panel(self) -> Panel:
        """Create the ASCII art panel."""
        art_lines = []
        for line in self.config.get("asciiArt", []):
            # Replace color codes with Rich markup
            for i in range(10):  # $0 to $9
                color_code = f"${i}"
                if color_code in line:
                    color = self._resolve_color(color_code)
                    line = line.replace(color_code, f"[{color}]")

            # Close any unclosed color tags and add reset
            art_lines.append(line + "[/]")

        art_text = "\n".join(art_lines)
        return Panel(art_text, box=box.MINIMAL, padding=(0, 1))

    def _create_side_panel(self) -> Panel:
        """Create the side text panel."""
        side_lines = []
        for item in self.config.get("sideText", []):
            color = self._resolve_color(item.get("color", "$1"))
            text = item.get("text", "")
            side_lines.append(f"[{color}]{text}[/]")

        side_text = "\n".join(side_lines)
        return Panel(side_text, box=box.MINIMAL, padding=(0, 1))

    def _render_static_banner(self):
        """Render the banner without animation."""
        art_text = self._create_art_text()
        side_text = self._create_side_text()

        # Print them separately for now to avoid encoding issues
        console.print(art_text)
        console.print()
        console.print(side_text)
        console.print()

    def _create_art_text(self) -> str:
        """Create the ASCII art text with colors."""
        art_lines = []
        for line in self.config.get("asciiArt", []):
            original_line = line
            # Replace color codes with Rich markup
            for i in range(10):  # $0 to $9
                color_code = f"${i}"
                if color_code in line:
                    color = self._resolve_color(color_code)
                    line = line.replace(color_code, f"[{color}]")

            # Close any unclosed color tags only if we added markup
            if line != original_line:
                art_lines.append(line + "[/]")
            else:
                art_lines.append(line)

        return "\n".join(art_lines)

    def _create_side_text(self) -> str:
        """Create the side text with colors."""
        side_lines = []
        for item in self.config.get("sideText", []):
            color = self._resolve_color(item.get("color", "$1"))
            text = item.get("text", "")
            side_lines.append(f"[{color}]{text}[/]")

        return "\n".join(side_lines)

    def display(self):
        """Display the startup banner."""
        if not self.config.get("boot", {}).get("showBanner", True):
            return

        # Check terminal size if configured to hide on small terminals
        if self.config.get("layout", {}).get("hideOnSmallTerminal", False):
            try:
                terminal_size = os.get_terminal_size()
                if terminal_size.columns < 80 or terminal_size.lines < 20:
                    return
            except OSError:
                pass  # Continue if we can't get terminal size

        # Always render static (no animation)
        self._render_static_banner()

        # Add a blank line after the banner
        console.print()


def show_startup_banner():
    """Convenience function to show the startup banner."""
    banner = StartupBanner()
    banner.display()
