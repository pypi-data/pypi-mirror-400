from enum import StrEnum

class MsgType(StrEnum):
    TEXT = "text"
    POST = "post"
    IMAGE = "image"
    INTERACTIVE = "interactive"
    AUDIO = "audio"
    MEDIA = "media"
    STICKER = "sticker"
    

class BotStatus(StrEnum):
    OK = "OK"
    FAILED = "FAILED"

class BotType(StrEnum):
    LARK = "lark"
    

