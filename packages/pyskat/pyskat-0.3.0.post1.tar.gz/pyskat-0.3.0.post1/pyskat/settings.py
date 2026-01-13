from typing import Annotated, Any
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import URL
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    TomlConfigSettingsSource,
)
from pathlib import Path
from functools import lru_cache
import click
from rich.traceback import install
from rich.highlighter import RegexHighlighter
import logging.config


class AccessHighlighter(RegexHighlighter):
    highlights = [
        r"\s(?P<bright_white>1\d\d)\s",
        r"\s(?P<green>2\d\d)\s",
        r"\s(?P<yellow>3\d\d)\s",
        r"\s(?P<red>4\d\d)\s",
        r"\s(?P<bright_red>5\d\d)\s",
    ]


DEFAULT_LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(message)s",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "format": "%(client_addr)s - %(request_line)s --> %(status_code)s",
            "use_colors": False,
        },
    },
    "handlers": {
        "pyskat": {
            "formatter": "default",
            "class": "rich.logging.RichHandler",
            "markup": True,
        },
        "uvicorn_default": {
            "formatter": "default",
            "class": "rich.logging.RichHandler",
        },
        "uvicorn_access": {
            "formatter": "access",
            "class": "rich.logging.RichHandler",
            "highlighter": AccessHighlighter(),
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["uvicorn_default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {
            "handlers": ["uvicorn_access"],
            "level": "INFO",
            "propagate": False,
        },
        "pyskat": {"handlers": ["pyskat"], "level": "INFO", "propagate": False},
    },
}

SUPPRESS_TRACEBACKS = [click]
install(show_locals=False, suppress=SUPPRESS_TRACEBACKS)


class EvaluationSettings(BaseModel):
    won_score: int = 50
    lost_score: int = -50
    opponent_lost_scores: dict[int, int] = {
        4: 30,
        3: 40,
    }
    game_score_multiplier: int = 1

    def get_opponent_lost_score(self, match_size: int):
        result = self.opponent_lost_scores.get(match_size, None)

        if result is None:
            raise ValueError(
                f"Opponent lost score for a match size of {match_size} has not been configured."
            )

        return result


class WuiSettings(BaseModel):
    theme: str = "darkly"
    plotly_template: str | dict = theme
    additional_template_dirs: list[Path] = []
    evaluation_displays: list[str] = [
        "evaluation_displays/table.html",
        "evaluation_displays/plot_scores.html",
        "evaluation_displays/plot_won.html",
        "evaluation_displays/plot_lost.html",
        "evaluation_displays/plot_opponents_lost.html",
    ]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PYSKAT_",
        env_nested_delimiter="__",
        toml_file="pyskat.toml",
    )

    database_url: str | URL = "sqlite:///pyskat.db"
    session_secret: str = "CHANGE_ME"

    wui: WuiSettings = WuiSettings()
    evaluation: EvaluationSettings = EvaluationSettings()
    logging: dict[str, Any] = DEFAULT_LOGGING_CONFIG

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            TomlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


@lru_cache
def settings_dep() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(settings_dep)]


logging.config.dictConfig(settings_dep().logging)
