"""
CLI entry point for Ameck Copilot
"""

import os
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint

console = Console()

CONFIG_DIR = Path.home() / ".ameck-copilot"
CONFIG_FILE = CONFIG_DIR / "config.env"


def get_api_key() -> str | None:
    """Get API key from config file or environment"""
    # First check environment variable
    if os.environ.get("GROQ_API_KEY"):
        return os.environ.get("GROQ_API_KEY")
    
    # Then check config file
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                if line.startswith("GROQ_API_KEY="):
                    key = line.strip().split("=", 1)[1].strip('"\'')
                    if key and key != "your_groq_api_key_here":
                        return key
    return None


def save_api_key(api_key: str) -> None:
    """Save API key to config file"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    config_content = f'''# Ameck Copilot Configuration
# Get your FREE API key at https://console.groq.com/keys

GROQ_API_KEY={api_key}
'''
    with open(CONFIG_FILE, "w") as f:
        f.write(config_content)
    
    # Set restrictive permissions (owner only)
    CONFIG_FILE.chmod(0o600)
    console.print(f"[green]✓[/green] API key saved to {CONFIG_FILE}")


def setup_api_key() -> str | None:
    """Interactive setup for API key"""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Ameck Copilot Setup[/bold cyan]\n\n"
        "To use Ameck Copilot, you need a [bold]FREE[/bold] Groq API key.\n"
        "Get yours at: [link=https://console.groq.com/keys]https://console.groq.com/keys[/link]",
        border_style="cyan"
    ))
    console.print()
    
    api_key = Prompt.ask(
        "[yellow]Enter your Groq API key[/yellow]",
        password=True
    )
    
    if not api_key or not api_key.startswith("gsk_"):
        console.print("[red]✗ Invalid API key. Groq API keys start with 'gsk_'[/red]")
        return None
    
    if Confirm.ask("Save API key for future use?", default=True):
        save_api_key(api_key)
    
    return api_key


def print_banner():
    """Print the application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     █████╗ ███╗   ███╗███████╗ ██████╗██╗  ██╗           ║
    ║    ██╔══██╗████╗ ████║██╔════╝██╔════╝██║ ██╔╝           ║
    ║    ███████║██╔████╔██║█████╗  ██║     █████╔╝            ║
    ║    ██╔══██║██║╚██╔╝██║██╔══╝  ██║     ██╔═██╗            ║
    ║    ██║  ██║██║ ╚═╝ ██║███████╗╚██████╗██║  ██╗           ║
    ║    ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝           ║
    ║                                                           ║
    ║              🤖 COPILOT - AI Coding Assistant             ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the FastAPI server"""
    import uvicorn
    
    # Set up environment for the app
    api_key = get_api_key()
    if not api_key:
        api_key = setup_api_key()
        if not api_key:
            console.print("[red]Cannot start without a valid API key.[/red]")
            sys.exit(1)
    
    os.environ["GROQ_API_KEY"] = api_key
    
    print_banner()
    console.print(f"\n[green]✓[/green] Starting Ameck Copilot on [bold]http://{host}:{port}[/bold]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")
    
    # Open browser automatically
    import webbrowser
    import threading
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open(f"http://{host}:{port}")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run(
        "ameck_copilot.app.main:app",
        host=host,
        port=port,
        log_level="info"
    )


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        prog="ameck-copilot",
        description="AI-powered coding assistant with a beautiful web interface"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command (default)
    run_parser = subparsers.add_parser("run", help="Start the Ameck Copilot server")
    run_parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    run_parser.add_argument("--port", "-p", type=int, default=8000, help="Port to bind to (default: 8000)")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Configure Ameck Copilot (set API key)")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Show current configuration")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        setup_api_key()
    elif args.command == "config":
        api_key = get_api_key()
        if api_key:
            masked_key = api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:]
            console.print(f"[green]✓[/green] API Key: {masked_key}")
            console.print(f"[dim]Config file: {CONFIG_FILE}[/dim]")
        else:
            console.print("[yellow]No API key configured. Run 'ameck-copilot setup' to configure.[/yellow]")
    elif args.command == "run" or args.command is None:
        host = getattr(args, "host", "127.0.0.1")
        port = getattr(args, "port", 8000)
        run_server(host=host, port=port)


if __name__ == "__main__":
    main()
