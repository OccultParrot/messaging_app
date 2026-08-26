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

console.rule("[bold green]OccultParrot's Messaging App[/bold green]")

console.print("[blue]Please enter your username:[/blue] ", end="")

username = input()

response = requests.get(f"{API_URL}/auth/{username}")

user_data = {}

if response.status_code == 200:
    user_data = response.json()
    console.print(f"[green]Welcome back, {username}![/green]")

elif response.status_code == 404:
    console.print(f"[yellow]Username '{username}' not found. Creating a new account...[/yellow]")
    console.print("[blue]What color do you want to be?[/blue][gray] (Enter hex color WITH #)[/gray] ", end="")

    color = input()

    console.print("[green]Creating your account...[/green]")
    response = requests.post(f"{API_URL}/users", json={"username": username, "color": color})
    user_data = response.json()


user_id = user_data.get("user_id")

console.print("Opening the chat interface...")
time.sleep(3)