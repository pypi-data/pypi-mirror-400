# PySkat - A Skat Tournament Management Program

![PySkat Logo](assets/pyskat_logo.svg)

PySkat is a web application for managing tournaments of the German national card game Skat. The functionality follows
the [official tournament rules](https://dskv.de/app/uploads/sites/43/2022/11/ISkO-2022.pdf) given by
the [Deutscher Skatverband e.V.](https://dskv.de) (German Skat Association). Evaluation of games is oriented at
the [official game sheets](https://dskv.de/app/uploads/sites/43/2020/11/Spiellisten.pdf) for tournaments.

## Current Status

This software is currently in **alpha** state, thus is functionality is not complete and the API may or will change in
future.

The following features are already working:

- ORM data model based on [SQLmodel](https://sqlmodel.tiangolo.com/)
- REST API for manipulating the database based on [FastAPI](https://fastapi.tiangolo.com/)
- Web interface for data display and comfortably talking to the API

The following planned features are **not** working:

- Data model on a per-game basis (currently per-match)
- Security features to manage data edit rights

## Installation

The software is published on PyPI and can be installed via `pip` or similar tools:

```shell
pip install pyskat
```

## Usage

Once installed, run the CLI using the `pyskat` command.

To show the help on available commands run:

```shell
pyskat --help
```

To run a webserver serving the API only:

```shell
pyskat serve-api
```

To run a webserver serving the web interface (including the api on `https://<host>/api`):

```shell
pyskat serve-wui
```

For help on available options use the `--help` option on these commands.
The option set is basically the same as for the `fastapi run` command (has been copied an adapted from there).
As with `fastapi run`, the ASGI server used is `uvicorn`, so it may be used in production.
Automatic OpenAPI documentation can be accessed at the `http://<host>/docs` resp. `http://<host>/api/docs` paths.

# License

This software is published under the terms of the [MIT License](LICENSE).
The SVG drawings in the `./assets` directory are licensed under the terms of the [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0).

# Contributing

This project is in early status and does currently not accept code contributions. This may change in future. Feedback
and suggestions are welcome via issues.
