import time

from rich.console import Console
import rich
import json
import requests
import websockets


BACKEND_URL = "https://api.occultparrot.dev"
API_URL = "https://api.occultparrot.dev/api"
WEBSOCKET_URL = "wss://api.occultparrot.dev/ws"

console = Console()
user_data = {}

console.rule("[bold green]OccultParrot's Messaging App[/bold green]")
while True:
    console.print("[blue]Please enter your username:[/blue] ", end="")
    username = input()

    response = requests.get(f"{API_URL}/auth/{username}")

    if response.status_code == 200:
        user_data = response.json()
        console.print(f"[green]Welcome back, [{user_data.get("color")}]{username}[/{user_data.get("color")}]![/green]")
        break;

    elif response.status_code == 400:
        console.print(f"[red]User {username} taken! Please try again.")
        continue

    elif response.status_code == 404:
        console.print(f"[yellow]Username '{username}' not found. Creating a new account...[/yellow]")
        console.print("[blue]What [red]c[/red][yellow]o[/yellow][green]l[/green][blue]o[/blue][purple]r[/purple] do you want to be?[/blue][gray] (Enter hex color WITH #)[/gray] ", end="")

        color = input()

        console.print("[green]Creating your account...[/green]")
        response = requests.post(f"{API_URL}/users", json={"username": username, "color": color})
        user_data = response.json()
        break;

    else:
        console.print(f"[red]Unknown error code: {response.status_code}, contact OccultParrot.")


user_id = user_data.get("id")

console.print("Opening the chat interface...")
time.sleep(3)