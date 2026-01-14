import random
from contextlib import contextmanager
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

QUOTES = [
    "Security is a process, not a product.",
    "The quieter you become, the more you are able to hear.",
    "There is no patch for human stupidity.",
    "Trust, but verify.",
    "Amateurs hack systems, professionals hack people.",
]

SENTINELX_LOGO = r"""
   _____            _   _            _ __   __
  / ____|          | | (_)          | |\ \ / /
 | (___   ___ _ __ | |_ _ _ __   ___| | \ V / 
  \___ \ / _ \ "_ \| __| | "_ \ / _ \ |  > <  
  ____) |  __/ | | | |_| | | | |  __/ | / . \ 
 |_____/ \___|_| |_|\__|_|_| |_|\___|_|/_/ \_\\
"""

SUB_BANNERS = {
    "main": "      [ One Console. All Teams. ]",
    "red": "      [ RED TEAM : OFFENSIVE OPS ]",
    "blue": "      [ BLUE TEAM : DEFENSIVE OPS ]",
    "purple": "      [ PURPLE TEAM : JOINT LABS ]"
}

BANNERS_COLORS = {
    "main": "cyan",
    "red": "red",
    "blue": "blue",
    "purple": "magenta",
}

def print_dynamic_banner(role="main"):
    color = BANNERS_COLORS.get(role, "green")
    
    # Center the Logo
    logo_text = Text(SENTINELX_LOGO, style=f"bold {color}")
    console.print(Align.center(logo_text))
    
    # Center the Sub-Banner
    sub_text_str = SUB_BANNERS.get(role, SUB_BANNERS["main"])
    sub_text = Text(sub_text_str, style=f"bold italic {color}")
    console.print(Align.center(sub_text))
    
    # Center the Quote
    quote = random.choice(QUOTES)
    console.print(Align.center(Text(f"\"{quote}\"", style="italic dim")))
    
    # Center the Mode Panel
    mode_panel = Panel.fit(f"SENTINELX v2.4 - {role.upper()} MODE", border_style=color)
    console.print(Align.center(mode_panel))

@contextmanager
def animated_spinner(message="Processing...", style="cyan"):
    with console.status(f"[bold {style}]{message}[/bold {style}]", spinner="dots"):
        yield
