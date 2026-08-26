from rich.console import Console
import rich
import json
import requests
import websockets


BACKEND_URL = "https://api.occultparrot.dev"
API_URL = "https://api.occultparrot.dev/api"
WEBSOCKET_URL = "wss://api.occultparrot.dev/ws"

console = Console()

console.rule("[bold green]OccultParrot's Messaging App[/bold green]")

console.print("[blue]Please enter your username:[/blue] ", end="")

username = input()

response = requests.get(f"{API_URL}/auth/{username}")
user_data = response.json()

if response.status_code == 200:
    console.print(f"[green]Welcome back, {user_data['username']}![/green]")