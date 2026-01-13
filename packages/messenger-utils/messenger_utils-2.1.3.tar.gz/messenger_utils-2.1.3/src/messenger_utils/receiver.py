"""
Parcing and processing messenger's responses and web-hooks
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps

### CLASS `Receiver` ###

class Receiver(ABC):
    """
    Receiver abstract class - parcing and processing responses and web-hooks.
    Particular functionality is implemented in derived classes.
    """

    def __init__(self, bot_token: str|None = None):
        """
        Init Receiver object.
        """
        self.bot_token: str|None = bot_token
        self.api_url: str = ""
        # Decorated function pointers for webhooks
        # Commands
        self.commands_table: dict[str, Callable] = {}               # Command <=> Function link (set by decorator `command``)
        # Messages
        self.create_message_func: Callable | None = None
        self.callback_messages_table: dict[str, Callable] = {}      # Button's token <=> Function link (set by decorator `callback`)
        # Functions processing bot state changes
        self.bot_started_func: Callable | None = None
        self.bot_stopped_func: Callable | None = None
        self.chat_cleared_func: Callable | None = None
        self.chat_removed_func: Callable | None = None



    #
    # DECORATORS FACTORY
    #


    def command(self, cmd_name: str) -> Callable:
        """
        Decorator factory for commands processing.
        
        :param name: command name (without /) to process
        :return: Decorator function
        """
        def decorator(func: Callable) -> Callable:
            """The decorator itself."""
            self.commands_table[cmd_name] = func
            @wraps(func)
            def wrapper(*args, **kwargs) -> Callable:
                """Wrapper function."""
                return func(*args, **kwargs)
            return wrapper
        return decorator



    def callback(self, btn_token: str) -> Callable:
        """
        Decorator for `callback_message` processing function.
        
        :return: Decorator function
        """
        def decorator(func: Callable) -> Callable:
            """The decorator itself."""
            self.callback_messages_table[btn_token] = func
            @wraps(func)
            def wrapper(*args, **kwargs) -> Callable:
                """Wrapper function."""
                return func(*args, **kwargs)
            return wrapper
        return decorator



    #
    # SIMPLE DECORATORS
    #


    def create_message(self, func: Callable) -> Callable:
        """
        Decorator for `create_message` processing function.
        
        :return: Wrapped function
        """
        self.create_message_func = func
        return func



    def bot_started(self, func: Callable) -> Callable:
        """
        Decorator for `bot_started` processing function.
        
        :return: Wrapped function
        """
        self.bot_started_func = func
        return func



    def bot_stopped(self, func: Callable) -> Callable:
        """
        Decorator for `bot_stopped` processing function.
        
        :return: Wrapped function
        """
        self.bot_stopped_func = func
        return func



    def chat_cleared(self, func: Callable) -> Callable:
        """
        Decorator for `chat_cleared` processing function.
        
        :return: Wrapped function
        """
        self.chat_cleared_func = func
        return func



    def chat_removed(self, func: Callable) -> Callable:
        """
        Decorator for `chat_removed` processing function.
        
        :return: Wrapped function
        """
        self.chat_removed_func = func
        return func



    #  PUBLIC METHODS


    @abstractmethod
    async def parse_webhook(self, body: dict) -> dict:
        """
        Parse message provided in webhooks requests.
        
        :param message: JSON-formatted message from messenger's webhook API
        """
        pass
