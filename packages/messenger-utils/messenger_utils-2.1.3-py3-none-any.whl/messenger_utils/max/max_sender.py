"""
Sender functionality for MAX messenger.

Contains class MaxSender, derived from Sender abstract class.
"""

import json
from typing import Any
import warnings
from messenger_utils.sender import Sender
from messenger_utils.max.max_keyboard import *
from . import MAX_API_URL


###   Class MaxSender   ###

class MaxSender(Sender):
    """
    Sender class for MAX messenger.
    
    Derived from Sender abstract class.
    """

    def __init__(
        self,
        bot_token: str
    ):
        """
        Constructor.
        
        :param secret_key: Secret key for API authentication.
        """
        if bot_token is None:
            raise ValueError("`bot_token` must be provided in constructor or in environment variable")
        super().__init__(bot_token)
        self.api_url = MAX_API_URL



    ### Public Interfaces ###

    # Bot info & settings

    async def get_bot_info(self) -> dict:
        """
        Get info about the MAX Bot.
        """
        endpoint = "me"
        response = await self.get(endpoint)
        return response



    async def get_webhooks(self) -> dict:
        """
        Get webhooks for the MAX Bot.
        """
        endpoint = "subscriptions"
        response = await self.get(endpoint)
        return response



    async def start_webhooks(self, url: str) -> dict:
        """
        Start webhooks for the MAX Bot.

        :param url: address of the webhooks processing server    
        """
        endpoint = "subscriptions"
        body = { "url": url }
        response = await self.post(endpoint, data=body)
        return response



    async def remove_webhook(self, url: str) -> dict:
        """
        Remove existing webhook for the MAX Bot.
        """
        endpoint = "subscriptions"
        params = { "url": url }
        response = await self.delete(endpoint, url_params=params)
        return response



    async def get_bot_commands(self) -> list[dict]:
        """
        Get list of bot commands.
        """
        endpoint = "me"
        response = await self.get(endpoint)
        if "commands" in response:
            return response["commands"]
        return []
    


    async def register_command(self, *, name: str, description: str):
        """
        Register new command for the MAX Bot (/xxx).
        
        :param name: command name (without /)
        :param description: Command description
        """
        endpoint = "me"
        commands = await self.get_bot_commands()
        # Check if command already exists
        for command in commands:
            if command["name"] == name:
                raise ValueError(f"Command `{name}` already exists")
        # Register new command
        new_command = {
            "name": name,
            "description": description
        }
        commands.append(new_command)
        data = {
            "commands": commands
        }
        response = await self.patch(endpoint, data=data)
        return response



    async def remove_command(self, *, name: str):
        """
        Remove command from the MAX Bot.
        
        :param name: command name (without /)
        :raises ValueError: If command not found
        :raises httpx.NetworkError: If there's a network-related error during the request.
        """
        endpoint = "me"
        commands = await self.get_bot_commands()
        # Remake the commands list without element with key = <name> by list comprehension
        commands2 = [command for command in commands if command["name"] != name]
        # If nothing happened print "nothing happened"
        if commands == commands2:
            raise ValueError(f"Command `{name}` not found")
        data = {
            "commands": commands2
        }
        response = await self.patch(endpoint, data=data)
        return response


    # Messages

    # pylint: disable=arguments-differ
    async def send_message(
            self,
            text: str, *,
            target: int,
            image_url: str|None = None,
            keyboard: MaxKeyboard|None = None,
            **kwargs
    ) -> dict:
        """
        Send message to the MAX user / chat.
        
        :param message: text of the message
        :param target: chat_id
        :param attachments: list of attachments
        """
        endpoint = "messages"
        data: dict[str, Any] = {
            "text": text,
            "format": "markdown"
        }
        if image_url:
            data["attachments"] = [
                {
                    "type": "image",
                    "payload": {
                        "url": image_url
                    }
                }
            ]
        if keyboard:
            if "attachments" not in data:
                data["attachments"] = []
            data["attachments"].append({
                "type": "inline_keyboard",
                "payload": json.loads(keyboard.to_json())
            })
        response = await self.post(endpoint, data=data, url_params={"chat_id": target})
        return response



    ### DEPRECATED! ###
    async def send_text_message(self, text: str, target: int) -> dict:
        """
        Send text message to the MAX user / chat via API.
        WARNING: Deprecated! Use `send_message` instead.
        
        :param message: text message to send
        :param target: chat_id
        :raises httpx.NetworkError: If there is a network-related error during the request.
        """
        warnings.warn("Deprecated! Use `send_message` instead.", category=DeprecationWarning, stacklevel=2)
        endpoint = "messages"
        data = {
            "text": text,
            "format": "markdown"
        }
        response = await self.post(endpoint, data=data, url_params={"chat_id": target})
        return response



    ### DEPRECATED! ###
    async def send_keyboard_message(self, text: str, target: int, keyboard: MaxKeyboard) -> dict:
        """
        Send message with inline keyboard to the MAX user / chat via API.
        WARNING: Deprecated! Use `send_message` instead.

        :param message: text message to send
        :param target: chat_id
        :keyboard: 2d-array of buttons       
        """
        warnings.warn("Deprecated! Use `send_message` instead.", category=DeprecationWarning, stacklevel=2)
        endpoint = "messages"
        data = {
            "text": text,
            "format": "markdown",
            "attachments": [
                {
                    "type": "inline_keyboard",
                    "payload": json.loads(keyboard.to_json())
                }
            ]
        }
        response = await self.post(endpoint, data=data, url_params={"chat_id": target})
        return response


    ### DEPRECATED! ###
    async def send_image_message(self, text: str, image_url: str, target: int) -> dict:
        """
        Send message with image attached by URL to the MAX user / chat.
        WARNING: Deprecated! Use `send_message` instead.
        """
        warnings.warn("Deprecated! Use `send_message` instead.", category=DeprecationWarning, stacklevel=2)
        endpoint = "messages"
        data = {
            "text": text,
            "format": "markdown",
            "attachments": [
                {
                    "type": "image",
                    "payload": {
                        "url": image_url
                    }
                }
            ]
        }
        response = await self.post(endpoint, data=data, url_params={"chat_id": target})
        return response


###   End of class MaxSender   ###
