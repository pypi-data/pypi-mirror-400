import os

from tortoise import Tortoise
from yarl import URL

from .models import ExtractedPage

MODELS_MODULES: list[str] = ["database.models"]


def get_db_url() -> str:
    db_host: str = os.environ.get("GRABBER_DB_HOST", "0.0.0.0")
    db_port: int = int(os.environ.get("GRABBER_DB_PORT", "5432"))
    db_user: str = os.environ.get("GRABBER_DB_USER", "postgres")
    db_pass: str = os.environ.get("GRABBER_DB_PASSWORD", "grabber_db")
    db_base: str = os.environ.get("GRABBER_DB_BASE", "grabber")

    url = URL.build(
        scheme="postgres",
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_pass,
        path=f"/{db_base}",
    )
    return str(url)


async def init_database():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(db_url=get_db_url(), modules={"models": MODELS_MODULES + ["aerich.models"]})
    # Generate the schema
    await Tortoise.generate_schemas()
