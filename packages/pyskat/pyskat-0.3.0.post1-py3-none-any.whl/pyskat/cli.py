import typer
import uvicorn
from typing import Annotated, Union
from pathlib import Path
from pyskat.settings import settings_dep

cli = typer.Typer(rich_markup_mode="rich")


@cli.command()
def serve_api(
    host: Annotated[
        str,
        typer.Option(
            help="The host to serve on. For local development in localhost use [blue]127.0.0.1[/blue]. To enable public access, e.g. in a container, use all the IP addresses available with [blue]0.0.0.0[/blue]."
        ),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option(
            help="The port to serve on. You would normally have a termination proxy on top (another program) handling HTTPS on port [blue]443[/blue] and HTTP on port [blue]80[/blue], transferring the communication to your app.",
            envvar="PORT",
        ),
    ] = 8000,
    reload: Annotated[
        bool,
        typer.Option(
            help="Enable auto-reload of the server when (code) files change. This is [bold]resource intensive[/bold], use it only during development."
        ),
    ] = False,
    root_path: Annotated[
        str,
        typer.Option(
            help="The root path is used to tell your app that it is being served to the outside world with some [bold]path prefix[/bold] set up in some termination proxy or similar."
        ),
    ] = "",
    proxy_headers: Annotated[
        bool,
        typer.Option(
            help="Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to populate remote address info."
        ),
    ] = True,
    forwarded_allow_ips: Annotated[
        Union[str, None],
        typer.Option(
            help="Comma separated list of IP Addresses to trust with proxy headers. The literal '*' means trust everything."
        ),
    ] = None,
    workers: Annotated[
        Union[int, None],
        typer.Option(help="Count of worker threads to use for serving."),
    ] = None,
):
    """Serve the Application Programming Interface (API) of PySkat."""
    uvicorn.run(
        app="pyskat.api:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        root_path=root_path,
        proxy_headers=proxy_headers,
        forwarded_allow_ips=forwarded_allow_ips,
        log_config=settings_dep().logging,
    )


@cli.command()
def serve_wui(
    host: Annotated[
        str,
        typer.Option(
            help="The host to serve on. For local development in localhost use [blue]127.0.0.1[/blue]. To enable public access, e.g. in a container, use all the IP addresses available with [blue]0.0.0.0[/blue]."
        ),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option(
            help="The port to serve on. You would normally have a termination proxy on top (another program) handling HTTPS on port [blue]443[/blue] and HTTP on port [blue]80[/blue], transferring the communication to your app.",
            envvar="PORT",
        ),
    ] = 8000,
    reload: Annotated[
        bool,
        typer.Option(
            help="Enable auto-reload of the server when (code) files change. This is [bold]resource intensive[/bold], use it only during development."
        ),
    ] = False,
    root_path: Annotated[
        str,
        typer.Option(
            help="The root path is used to tell your app that it is being served to the outside world with some [bold]path prefix[/bold] set up in some termination proxy or similar."
        ),
    ] = "",
    proxy_headers: Annotated[
        bool,
        typer.Option(
            help="Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to populate remote address info."
        ),
    ] = True,
    forwarded_allow_ips: Annotated[
        Union[str, None],
        typer.Option(
            help="Comma separated list of IP Addresses to trust with proxy headers. The literal '*' means trust everything."
        ),
    ] = None,
    workers: Annotated[
        Union[int, None],
        typer.Option(help="Count of worker threads to use for serving."),
    ] = None,
):
    """Serve the Web User Interface (WUI) of PySkat. The API is served on a subpath alongside."""
    uvicorn.run(
        app="pyskat.wui:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        root_path=root_path,
        proxy_headers=proxy_headers,
        forwarded_allow_ips=forwarded_allow_ips,
        log_config=settings_dep().logging,
    )


@cli.command()
def init(
    dir: Annotated[
        Path | None,
        typer.Option(
            help="Optionally specify a working directory, default is the current working directory."
        ),
    ] = None,
):
    """Create the config file `pyskat.toml` in the working directory with the default config."""
    from pyskat.settings import Settings
    from tomli_w import dumps

    dir = dir or Path.cwd()
    dir.mkdir(parents=True, exist_ok=True)
    file = dir / "pyskat.toml"

    if file.exists():
        typer.confirm(
            f"Overwrite existing config file {file.absolute()}",
            prompt_suffix="? ",
            abort=True,
        )

    file.write_text(dumps(Settings().model_dump(mode="json")))
