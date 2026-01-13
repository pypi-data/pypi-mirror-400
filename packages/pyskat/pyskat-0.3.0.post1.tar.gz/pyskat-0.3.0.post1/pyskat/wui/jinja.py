from pathlib import Path
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
from pyskat.settings import settings_dep, SettingsDep
from pyskat.wui.messages import get_flashed_messages
from typing import Annotated, Callable, Concatenate
from fastapi import Depends

TEMPLATE_DIR = Path(__file__).parent / "templates"


def settings_processor(request):
    return dict(settings=settings_dep())


def messages_processor(request):
    return dict(get_flashed_messages=lambda: get_flashed_messages(request))


def render_template(request: Request, settings: SettingsDep):
    templates = Jinja2Templates(
        directory=[TEMPLATE_DIR] + settings.wui.additional_template_dirs,
        context_processors=[settings_processor, messages_processor],
    )

    def create_template_response(template_name: str, **kwargs):
        return templates.TemplateResponse(request, template_name, context=kwargs)

    return create_template_response


RenderTemplateDep = Annotated[
    Callable[Concatenate[str, ...], _TemplateResponse], Depends(render_template)
]
