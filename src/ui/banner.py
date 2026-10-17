from rich.console import Console
from rich.text import Text

console = Console()

BANNER_ART = r"""
     _ _                       _       _                             
  __| (_)___  ___ ___  _ __ __| |  ___| | ___  _ __   ___ _ __ 
 / _` | / __|/ __/ _ \| '__/ _` | / __| |/ _ \| '_ \ / _ \ '__|
| (_| | \__ \ (_| (_) | | | (_| || (__| | (_) | | | |  __/ |   
 \__,_|_|___/\___\___/|_|  \__,_| \___|_|\___/|_| |_|\___|_|   
"""

def print_banner():
    console.clear()
    banner = Text(BANNER_ART, style="bold cyan")
    sub = Text(" discord-server-cloner | v1.0.0\n", style="dim white")
    console.print(banner)
    console.print(sub)
