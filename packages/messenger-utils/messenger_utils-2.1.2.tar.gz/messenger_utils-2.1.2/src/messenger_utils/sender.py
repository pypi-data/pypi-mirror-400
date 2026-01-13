"""
Message send functionality for messenger_utils
"""

from abc import ABC, abstractmethod
import httpx


### CLASS `Sender` ###

class Sender(ABC):
    """
    Sender abstract class to send messages to messenger via API.
    Particular functionality is implemented in derived classes.
    """

    def __init__(self, bot_token: str):
        """
        Init Sender object.
        
        :param secret_key: Secret key for API authentication.
        """
        self.bot_token: str = bot_token
        self.api_url: str = ""



    @abstractmethod
    async def send_message(
            self,
            text: str,
            **kwargs
    ) -> dict:
        """
        Sends a message to the messenger's webhook URL.
        
        :param message: text message to send
        :param target: user_id, chat_id, etc. (see docs in derived classes)
        """
        pass


    ###  Network fucntionality  ###


    async def get(
        self,
        endpoint: str="", *,
        url_params: dict[str, str|int]|None = None
    ):
        """
        Send GET request to the bot API.
        
        :param endpoint: url part after `api_url`
        :param url-params: ?xxx&yyy params of get-request (if needed)
        """
        url = f"{self.api_url}/{endpoint}"
        headers = {
            "Authorization": self.bot_token
        }
        response: httpx.Response
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
                params=url_params
            )
            response.raise_for_status()
        return response.json()



    async def patch(
        self,
        endpoint: str="", *,
        data: dict|None = None
    ):
        """
        Send PATCH request to the bot API.

        :param: endpoint: url part after `api_url`
        :param: data: request body in dict format
        """
        url = f"{self.api_url}/{endpoint}"
        headers = {
            "Authorization": self.bot_token
        }
        response: httpx.Response
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                url,
                headers=headers,
                json=data
            )
            response.raise_for_status()
        return response.json()



    async def post(
        self,
        endpoint: str="", *,
        data: dict|None = None,
        url_params: dict[str, str|int]|None = None
    ):
        """
        Send POST request to the bot API.

        :param: endpoint: url part after `api_url`
        :param: data: request body in dict format
        """
        url = f"{self.api_url}/{endpoint}"
        headers = {
            "Authorization": self.bot_token
        }
        response: httpx.Response
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                params=url_params,
                json=data
            )
            response.raise_for_status()
        return response.json()



    async def delete(
        self,
        endpoint: str="", *,
        url_params: dict[str, str|int]|None = None
    ):
        """
        Send DELETE request to the bot API.

        :param: endpoint: url part after `api_url`
        """
        url = f"{self.api_url}/{endpoint}"
        headers = {
            "Authorization": self.bot_token
        }
        response: httpx.Response
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                url,
                headers=headers,
                params=url_params
            )
            response.raise_for_status()
        return response.json()


### END OF CLASS `SENDER`` ###
