import uvicorn
import logging


def test_serve(add_results, add_session, caplog, wui_app):
    caplog.set_level(logging.INFO)
    uvicorn.run(
        app=wui_app,
        host="127.0.0.1",
        port=8000,
    )
