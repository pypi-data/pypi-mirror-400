from dataclasses import dataclass
from .const import BotStatus

@dataclass
class BotResponse:
    status: BotStatus
    msg: str
    errors: str = ""
