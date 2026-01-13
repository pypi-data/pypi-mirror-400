"""
Messengers API Utils: 
CLI interface.

For help use:

Via pure python:
```python -m messenger_utils -h```

Via UV:
``` uv run -m uessenger_utils -h```
"""

from typing import Literal
import asyncio
import typer
from httpx import NetworkError
from rich.console import Console
from rich.table import Table
from messenger_utils import __version__
from messenger_utils.max import MaxSender



# Global objects
app = typer.Typer(
    name="Messenger Utils",
    help="Utilites and CLI tool for Telegram & MAX messengers.",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_markup_mode="rich"
)
console = Console(highlight=False)
ENV_PREFIX = "MESSENGER_UTILS_"

###  CLI commands  ###


@app.command()
def version():
    """Print package version."""
    console.print(__version__, style="cyan")



@app.command(name="bot-info")
def bot_info(
    bot_token: str = typer.Option(..., "--bot-token", "-t",  envvar=f"{ENV_PREFIX}MAX_BOT_TOKEN", show_envvar=True, help="MAX bot token"),
    messenger: Literal["max", "telegram"] = typer.Option("max", "--messenger", "-m", help="Messenger type")
):
    """Get information about the MAX or Telegram Bot."""
    if messenger == "max":
        sender = MaxSender(bot_token=bot_token)
        bot_info =  asyncio.run(sender.get_bot_info())
        console.print(bot_info, style="cyan")
    else:
        # TODO: bot information for Telegram bot
        pass



@app.command(name="webhooks")
def webhooks(
    bot_token: str = typer.Option(..., "--bot-token", "-t",  envvar=f"{ENV_PREFIX}MAX_BOT_TOKEN", show_envvar=True, help="MAX bot token"),
    set_url: str|None = typer.Option(None, "--set", help="Webhook URL to set"),
    remove_url: str|None = typer.Option(None, "--remove", help="Webhook URL to remove"),
):
    """
    Get or set webhooks processing servers.
    
    :param set_url: Webhook URL to set.
    :param remove_url: Existing webhook URL to unset.
    (if set_url and remove_url are not presented - info of current webhooks will be printed)
    """
    sender = MaxSender(bot_token=bot_token)
    if set_url is None and remove_url is None:
        hooks =  asyncio.run(sender.get_webhooks())
        for hook in hooks.get("subscriptions", []):
            console.print(f"[>] {hook['url']}", style="cyan")
    else:
        if set_url is not None:
            response =  asyncio.run(sender.start_webhooks(url=set_url))
            console.print("Set webhook:")
            console.print(response, style="cyan")
        if remove_url is not None:
            response =  asyncio.run(sender.remove_webhook(url=remove_url))
            console.print("Remove webhook:")
            console.print(response, style="cyan")



@app.command(name="bot-commands")
def bot_commands(
    bot_token: str = typer.Option(..., "--bot-token", "-t",  envvar=f"{ENV_PREFIX}MAX_BOT_TOKEN", show_envvar=True, help="MAX bot token"),
    messenger: Literal["max", "telegram"] = typer.Option("max", "--messenger", "-m", help="Messenger type")
):
    """Get list of bot commands."""
    if messenger == "max":
        sender = MaxSender(bot_token=bot_token)
        bot_commands =  asyncio.run(sender.get_bot_commands())
        # if bot_commands list is empty
        if not bot_commands:
            console.print("No commands found for bot", style="yellow")
            return
        table = Table(title="Bot Commands")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="cyan")
        for command in bot_commands:
            table.add_row(command.get("name", ""), command.get("description", ""))
        console.print(table)
    else:
        # TODO: bot commands for Telegram bot
        pass



@app.command(name="set-command")
def set_command(
    bot_token: str = typer.Option(..., "--bot-token", "-t",  envvar=f"{ENV_PREFIX}MAX_BOT_TOKEN", show_envvar=True, help="MAX bot token"),
    messenger: Literal["max", "telegram"] = typer.Option("max", "--messenger", "-m", help="Messenger type"),
    name: str = typer.Option(..., "--name", "-n", help="Command name", prompt=True),
    description: str = typer.Option(..., "--description", "-d", help="Command description", prompt=True)
):
    """Register new command for the Bot."""
    if messenger == "max":
        sender = MaxSender(bot_token=bot_token)
        try:
            response = asyncio.run(sender.register_command(name=name, description=description))
        except ValueError:
            console.print(f"[!] Command `{name}` already exists!", style="red")
            return
        console.print(response, style="cyan")
    else:
        # TODO: set command for Telegram bot
        pass



@app.command(name="remove-command")
def remove_command(
    bot_token: str = typer.Option(..., "--bot-token", "-t",  envvar=f"{ENV_PREFIX}MAX_BOT_TOKEN", show_envvar=True, help="MAX bot token"),
    messenger: Literal["max", "telegram"] = typer.Option("max", "--messenger", "-m", help="Messenger type"),
    names: list[str] = typer.Option([], "--name", "-n", help="Command name")
):
    """Remove command from the Bot."""
    if not names:
        console.print("[!] No commands provided!", style="red")
        raise typer.Abort()
    # MAX Messenger part
    if messenger == "max":
        sender = MaxSender(bot_token=bot_token)
        response: dict = {}
        for name in names:
            try:
                response = asyncio.run(sender.remove_command(name=name))
            except ValueError:
                console.print(f"[!] Command `{name}` not found!", style="red")
                return
        console.print(response, style="cyan")
    # Telegram part
    else:
        # TODO: remove command for Telegram bot
        pass



@app.command(name="send")
def send_message(
    bot_token: str = typer.Option(..., "--bot-token", "-t",  envvar=f"{ENV_PREFIX}MAX_BOT_TOKEN", show_envvar=True, help="MAX bot token"),
    messenger: Literal["max", "telegram"] = typer.Option("max", "--messenger", "-m", help="Messenger type"),
    target: str = typer.Option(..., "--chat", "-c", help="Chat ID for MAX"),
    content: str = typer.Argument(..., help="Message to send")
    # content: str = typer.Option(..., "--message", "-c", help="Message to send", prompt=True),
):
    """Send message to the Bot."""
    # MAX part
    if messenger == "max":
        sender = MaxSender(bot_token=bot_token)
        try:
            response = asyncio.run(sender.send_text_message (text=content, target=target))
        except NetworkError:
            console.print("[!] Network error!", style="red")
            return
        console.print(response, style="cyan")
    # Telegram part
    else:
        # TODO: send command for Telegram bot
        pass





def main():
    """Entry point for CLI app."""
    app()

if __name__ == "__main__":
    main()
