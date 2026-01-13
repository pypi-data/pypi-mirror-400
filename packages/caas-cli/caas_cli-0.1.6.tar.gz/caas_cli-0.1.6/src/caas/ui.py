from __future__ import annotations

from contextlib import contextmanager
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.text import Text

THEME = Theme(
    {
        "ok": "bold green",
        "warn": "bold yellow",
        "bad": "bold red",
        "dim": "dim",
        "title": "bold cyan",
        "accent": "bold magenta",
    }
)

console = Console(theme=THEME)

BANNER = r"""                                                                                                                    
     ██       █████████████████     █   █                
   █████ ███████████████████████████████████████     █   
    ███ ██████████████████████████████████████████  ███  
  ██  ██████      ████████████████████       ██████ ███  
     █████     ████ █████████████████     ████ █████            ______     ______     ______     ______   
    █████      ████ ████████████████       ███  █████          /\  ___\   /\  __ \   /\  __ \   /\  ___\  
   ██████  ██       ████████████████  ██        █████  █       \ \ \____  \ \  __ \  \ \  __ \  \ \___  \    
    ██████ ███      █████████████████████      ██████           \ \_____\  \ \_\ \_\  \ \_\ \_\  \/\_____\
   █████████  ██   ███████████████████   ██  ████████            \/_____/   \/_/\/_/   \/_/\/_/   \/_____/
   ████████████████████ █████████ ████████████████████        
   ████████████████████           ███████████████████          Companion as a Service CLI • Solana • Pump.fun
    ████████████████████ ███████ ███████████████████     
       ██████████████████ ████  ██████████████████       
          ███████████████████████████████████            
                ██████████████████████                   
                          █████   

                          
© 2026 CAAS CLI"""


def show_banner() -> None:
    console.print(Panel(Text(BANNER, style="title"), border_style="accent"))


def rule(title: str) -> None:
    console.print(f"[dim]-------------------- {title} --------------------[/dim]")


def ok(msg: str) -> None:
    console.print(f"[ok][OK][/ok] {msg}")


def warn(msg: str) -> None:
    console.print(f"[warn][!][/warn] {msg}")


def bad(msg: str) -> None:
    console.print(f"[bad][X][/bad] {msg}")


def panel(title: str, body: str) -> None:
    console.print(Panel(body, title=f"[title]{title}[/title]", border_style="accent"))


@contextmanager
def spinner(message: str = "Thinking..."):
    with console.status(f"[accent]{message}[/accent]", spinner="line"):
        yield
