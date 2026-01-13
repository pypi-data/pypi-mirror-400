"""
Keyboard construction classes for MAX inline keyboards.
"""

import json
from enum import Enum
from dataclasses import dataclass, field, asdict

__all__ = [
    "BtnTypes", "BtnIntents", "ButtonUnion", "MaxKeyboard",
    "CallbackButton", "LinkButton", "RequestContactButton", "RequestGeoLocationButton", "OpenAppButton", "MessageButton"
]


# Button enums


class BtnTypes(Enum):
    """Types of buttons for MAX inline keyboard."""
    CALLBACK = "callback"
    LINK = "link"
    REQUEST_CONTACT = "request_contact"
    REQUEST_GEO_LOCATION = "request_geo_location"
    OPEN_APP = "open_app"
    MESSAGE = "message"

    def __str__(self):
        return self.value


class BtnIntents(Enum):
    """Intents of buttons for MAX inline keyboard."""
    DEFAULT = "default"
    NEGATIVE = "negative"
    POSITIVE = "positive"

    def __str__(self):
        return self.value


def json_enum_encoder(obj):
    """JSON encoder for enums."""
    if isinstance(obj, Enum):
        return obj.value
    return obj



# Button base class

@dataclass
class BaseButton:
    """
    Button for MAX messenger inline keyboard.
    """
    btn_type:   BtnTypes = field(init=False)
    text:       str

    def to_dict(self) -> dict:
        """Convert the button to a JSON-serializable dictionary."""
        btn_dict = asdict(self)
        return btn_dict
    
    def to_json(self) -> str:
        """Convert the button to a JSON string."""
        btn_dict = self.to_dict()
        return json.dumps(btn_dict, default=json_enum_encoder).replace("btn_type", "type")



# Button types classes


@dataclass
class CallbackButton(BaseButton):
    """Callback type button."""
    btn_type = BtnTypes.CALLBACK
    payload: str                               # Button's token (up to 1024 chars). WARNING: Should be identifier-style!
    intent:  BtnIntents = BtnIntents.DEFAULT   # Button's intent (affects the display on the client)


@dataclass
class LinkButton(BaseButton):
    """Link type button."""
    btn_type = BtnTypes.LINK
    url: str                                   # link url (up to 2048 chars)


@dataclass
class RequestContactButton(BaseButton):
    """Request contact type button."""
    btn_type = BtnTypes.REQUEST_CONTACT


@dataclass
class RequestGeoLocationButton(BaseButton):
    """Request geo location type button."""
    btn_type = BtnTypes.REQUEST_GEO_LOCATION
    quick: bool = False                        # If `True` - sends location without user's confirm


@dataclass
class OpenAppButton(BaseButton):
    """Open app type button."""
    btn_type = BtnTypes.OPEN_APP
    web_app:    str|None = None                # Bot's public name or link - owner of mini-app
    contact_id: int|None = None                # Bot's ID - owner of mini-app
    payload:    str|None = None                # Launch param, to be sent to initData of mini-app


@dataclass
class MessageButton(BaseButton):
    """Message type button."""
    btn_type = BtnTypes.MESSAGE


# Keyboard class

ButtonUnion = CallbackButton | LinkButton | RequestContactButton | RequestGeoLocationButton | OpenAppButton | MessageButton


@dataclass
class MaxKeyboard:
    """
    MAX messenger inline keyboard.
    """
    buttons: list[list[ButtonUnion]] = field(default_factory=list)



    def add_row(self, btn_row: list[ButtonUnion]):
        """Add a row of buttons to the keyboard."""
        self.buttons.append(btn_row)



    def to_dict(self) -> dict:
        """Convert the keyboard to a JSON-serializable dictionary."""
        keyboard_data = []
        for row in self.buttons:
            row_data = []
            for button in row:
                btn_dict = button.to_dict()
                row_data.append(btn_dict)
            keyboard_data.append(row_data)
        return {"buttons": keyboard_data}



    def to_json(self) -> str:
        """Convert the keyboard to a JSON string."""
        return json.dumps(self.to_dict(), default=json_enum_encoder).replace("btn_type", "type")
