import os

from yarl import URL

MODELS_MODULES: list[str] = ["src.database.models"]


def get_db_url() -> str:
    db_host: str = os.environ.get("GRABBER_HOST", "0.0.0.0")
    db_port: int = int(os.environ.get("GRABBER_PORT", "5432"))
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


TORTOISE_CONFIG = {
    "connections": {
        "default": get_db_url(),
    },
    "apps": {
        "models": {
            "models": MODELS_MODULES + ["aerich.models"],
            "default_connection": "default",
        },
    },
}
