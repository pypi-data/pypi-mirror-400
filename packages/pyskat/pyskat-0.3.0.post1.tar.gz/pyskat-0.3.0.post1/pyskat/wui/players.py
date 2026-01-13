from fastapi.routing import APIRouter
from sqlmodel import select

from pyskat.wui.jinja import RenderTemplateDep
from pyskat.database import DbSessionDep
from pyskat.data_model import Player


router = APIRouter(prefix="/players", tags=["player"])


@router.get("/")
def wui_players(render_template: RenderTemplateDep, db: DbSessionDep):
    players = db.exec(select(Player)).all()
    return render_template("players.html", players=players)
