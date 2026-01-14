#!/usr/bin/env python3
import sys
import os
from rich.console import Console

# Ensure the script can see the package if run locally
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from sentinelx.core.menu import main_menu
except ImportError:
    from .core.menu import main_menu

console = Console()

def main():
    try:
        # Use alternate screen buffer for "Takeover" effect
        with console.screen():
            main_menu()
    except KeyboardInterrupt:
        print("\nExiting SentinelX...")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Critical Error:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
