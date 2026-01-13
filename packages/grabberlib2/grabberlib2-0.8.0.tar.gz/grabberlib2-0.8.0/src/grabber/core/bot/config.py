from dataclasses import dataclass

from environs import Env
from telegraph import Telegraph

from grabber.core.settings import CHANNELS

env = Env()
env.read_env()


@dataclass
class BotSettings:
    bot_token: str
    channels: dict[str, str]
    telegraph_author_name: str | None = None
    telegraph_author_url: str | None = None
    telegraph_short_name: str | None = None
    telegraph_token: str | None = None
    __telegraph_client: Telegraph | None = None

    @property
    def telegraph_client(self) -> Telegraph:
        if not self.__telegraph_client and self.telegraph_token:
            self.__telegraph = Telegraph(access_token=self.telegraph_token)

        return self.__telegraph_client


def get_settings() -> BotSettings:
    token = env.str("BOT_TOKEN", "")
    telegraph_token = env.str("TELEGRAPH_TOKEN", "")
    short_name = env.str("SHORT_NAME", "")
    author_name = env.str("AUTHOR_NAME", "")
    author_url = env.str("AUTHOR_URL", "")

    if not token:
        raise RuntimeError("BOT_TOKEN not set")

    return BotSettings(
        bot_token=token,
        channels=CHANNELS,
        telegraph_author_name=author_name,
        telegraph_author_url=author_url,
        telegraph_short_name=short_name,
        telegraph_token=telegraph_token,
    )
