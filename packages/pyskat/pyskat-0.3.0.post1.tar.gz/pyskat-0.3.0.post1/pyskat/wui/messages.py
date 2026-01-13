from enum import StrEnum
from typing import Annotated, Callable
from pydantic import BaseModel, ConfigDict
from fastapi.requests import Request
from fastapi import Depends


class MessageCategory(StrEnum):
    PRIMARY = "primary"
    DANGER = "danger"
    ERROR = "danger"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


class Message(BaseModel):
    text: str
    category: MessageCategory

    model_config = ConfigDict(frozen=True)


def flash_message(request: Request, message: Message) -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append(message.model_dump_json())


def get_flashed_messages(request: Request):
    return (
        [Message.model_validate_json(m) for m in request.session.pop("_messages")]
        if "_messages" in request.session
        else []
    )


def flash_error_dep(request: Request):
    def flash_error(text: str):
        flash_message(request, Message(text=text, category=MessageCategory.ERROR))

    return flash_error


FlashErrorDep = Annotated[Callable[(str,), None], Depends(flash_error_dep)]


def flash_warning_dep(request: Request):
    def flash_warning(text: str):
        flash_message(request, Message(text=text, category=MessageCategory.WARNING))

    return flash_warning


FlashWarningDep = Annotated[Callable[(str,), None], Depends(flash_warning_dep)]


def flash_info_dep(request: Request):
    def flash_info(text: str):
        flash_message(request, Message(text=text, category=MessageCategory.INFO))

    return flash_info


FlashInfoDep = Annotated[Callable[(str,), None], Depends(flash_info_dep)]


def flash_success_dep(request: Request):
    def flash_success(text: str):
        flash_message(request, Message(text=text, category=MessageCategory.SUCCESS))

    return flash_success


FlashSuccessDep = Annotated[Callable[(str,), None], Depends(flash_success_dep)]
