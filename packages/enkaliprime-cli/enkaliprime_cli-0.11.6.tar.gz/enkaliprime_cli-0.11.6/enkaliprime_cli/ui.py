"""
UI components for the EnkaliPrime CLI.
Provides consistent styling matching the Fastfetch cyberpunk aesthetic.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.style import Style
from rich.layout import Layout
from rich import box
import platform
import psutil
import os
from . import __version__

console = Console()

# Theme Colors
COLOR_PRIMARY = "cyan"
COLOR_SECONDARY = "magenta"
COLOR_ACCENT = "green"
COLOR_DIM = "dim white"

FOX_ART = """
[magenta]    .::::::.[/]       [cyan].::::::.[/]
[magenta]  .::::::::::.[/]   [cyan].::::::::::.[/]
[magenta] .::::::::::::::.[/] [cyan].::::::::::::::.[/]
[magenta] .::::::::::::::.[/] [cyan].::::::::::::::.[/]
[magenta]  .::::::::::::.[/]   [cyan].::::::::::::.[/]
[magenta]    '::::::::'[/]       [cyan]'::::::::'[/]

[magenta]   .::[/][cyan]::.[/]   [magenta].::[/][cyan]::.[/]
[magenta] .::::[/][cyan]::::.[/] [magenta].::::[/][cyan]::::.[/]
"""

class Header:
    """Displays the CLI header with ASCII art and system info."""
    
    @staticmethod
    def draw(agent_name: str = "EnkaliPrime CLI"):
        grid = Table.grid(expand=True, padding=(0, 2))
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="left", ratio=2)
        
        # System Info Assembly
        sys_info = Table.grid(padding=(0, 1))
        sys_info.add_column(style=COLOR_PRIMARY, justify="right")
        sys_info.add_column(style="white")
        
        # Gather real info
        uname = platform.uname()
        mem = psutil.virtual_memory()
        
        rows = [
            ("User", f"[bold {COLOR_SECONDARY}]{os.getlogin()}[/]@[bold {COLOR_PRIMARY}]{uname.node}[/]"),
            ("OS", f"{uname.system} {uname.release} ({uname.machine})"),
            ("Host", uname.node),
            ("Kernel", uname.release),
            ("Uptime", "Just started"), # Placeholder or calc if needed
            ("Memory", f"{mem.used // (1024**2)} MiB / {mem.total // (1024**2)} MiB"),
            ("SDK", f"v{__version__}"),
        ]
        
        for label, value in rows:
            sys_info.add_row(f"{label}", value)
            
        color_dots = Text("● ● ● ● ● ● ● ●", style=f"bold {COLOR_SECONDARY}")

        # Combine Art and Info
        grid.add_row(
            Panel(FOX_ART, box=box.MINIMAL, border_style=COLOR_DIM),
            Panel(
                sys_info, 
                title=f"[bold {COLOR_PRIMARY}]{agent_name}[/]",
                subtitle=color_dots,
                border_style=COLOR_SECONDARY,
                box=box.ROUNDED
            )
        )
        
        console.print(grid)

def cyber_panel(content, title=None, style=COLOR_PRIMARY):
    """Creates a styled panel with the cyberpunk aesthetic."""
    return Panel(
        content,
        title=f"[bold {style}]{title}[/]" if title else None,
        border_style=style,
        box=box.ROUNDED,
        padding=(1, 2)
    )

def print_success(message: str):
    console.print(f"[bold {COLOR_ACCENT}]✓[/] {message}")

def print_error(message: str):
    console.print(f"[bold red]✗[/] {message}")

def print_warning(message: str):
    console.print(f"[bold yellow]![/] {message}")
