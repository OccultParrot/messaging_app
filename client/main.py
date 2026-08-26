import json
import time

import requests
import websockets
from rich.console import Console
from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Input, RichLog

BACKEND_URL = "https://api.occultparrot.dev"
API_URL = f"{BACKEND_URL}/api"
WEBSOCKET_URL = "wss://api.occultparrot.dev/ws"

console = Console()


def login() -> dict:
    console.rule("[bold green]OccultParrot's Messaging App[/bold green]")
    while True:
        console.print("[blue]Please enter your username:[/blue] ", end="")
        username = input()

        response = requests.get(f"{API_URL}/auth/{username}")

        if response.status_code == 200:
            user_data = response.json()
            color = user_data.get("color")
            console.print(f"[green]Welcome back, [{color}]{username}[/{color}]![/green]")
            return user_data

        elif response.status_code == 400:
            console.print(f"[red]User {username} taken! Please try again.")
            continue

        elif response.status_code == 404:
            console.print(f"[yellow]Username '{username}' not found. Creating a new account...[/yellow]")
            console.print(
                "[blue]What [red]c[/red][yellow]o[/yellow][green]l[/green][blue]o[/blue][purple]r[/purple] "
                "do you want to be?[/blue][gray] (Enter hex color WITH #)[/gray] ",
                end="",
            )

            color = input()

            console.print("[green]Creating your account...[/green]")
            response = requests.post(f"{API_URL}/users", json={"username": username, "color": color})
            return response.json()

        else:
            console.print(f"[red]Unknown error code: {response.status_code}, contact OccultParrot.")


class ChatApp(App):
    """Scrolling message log with an input pinned to the bottom of the screen."""

    CSS = """
    RichLog {
        height: 1fr;
        border: solid $accent;
        padding: 0 1;
    }

    Input {
        dock: bottom;
    }
    """

    def __init__(self, user_data: dict, **kwargs):
        super().__init__(**kwargs)
        self.user_data = user_data
        self.user_id = user_data.get("id")
        self.websocket = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="messages", wrap=True, markup=True, highlight=True)
        yield Input(placeholder="Type a message and press Enter...", id="message_input")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()
        self.connect_websocket()

    # Runs in the background so the UI stays responsive while we wait on incoming messages.
    @work(exclusive=True)
    async def connect_websocket(self) -> None:
        log = self.query_one(RichLog)
        try:
            async with websockets.connect(f"{WEBSOCKET_URL}?user_id={self.user_id}") as ws:
                self.websocket = ws
                log.write("[green]Connected to chat server.[/green]")
                async for raw_message in ws:
                    self.handle_incoming(raw_message, log)
        except Exception as e:
            log.write(f"[red]Connection error: {e}[/red]")

    def handle_incoming(self, raw_message: str, log: RichLog) -> None:
        try:
            data = json.loads(raw_message)
        except json.JSONDecodeError:
            log.write(raw_message)
            return

        username = data.get("username", "unknown")
        color = data.get("color", "white")
        content = data.get("message", "")
        log.write(f"[{color}]{username}[/{color}]: {content}")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()
        event.input.value = ""
        if not message or self.websocket is None:
            return

        log = self.query_one(RichLog)
        my_color = self.user_data.get("color", "white")
        log.write(f"[{my_color}]you[/{my_color}]: {message}")
        await self.websocket.send(json.dumps({"user_id": self.user_id, "message": message}))


if __name__ == "__main__":
    user_data = login()
    console.print("Opening the chat interface...")
    time.sleep(1)
    ChatApp(user_data).run()
