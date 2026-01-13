# mypy: disable-error-code="misc,has-type,operator,union-attr,attr-defined"
"""
How it works (flow)
        1.	User sends links (or uses /post Title …links…).
        2.	extract_urls() finds URLs in the message.
        3.	get_image_links_from_sources() — plug in your existing scraper here to turn those page links into direct image URLs.
        4.	build_telegraph_html() — builds HTML for the Telegraph page (swap with your own HTML/node generation).
        5.	Telegraph page is created; the bot shows the preview link + an inline keyboard of your channels.
        6.	When the user taps a channel, the bot posts the Telegraph link to that channel.

⸻

Important setup notes
        •	Add your bot to each target channel and make it Admin (at least permission to post messages).
        •	Channel IDs must be in the -100... format. You can obtain them by forwarding a message from the channel to @getidsbot or similar, or via the Bot API using chat.id.
        •	If you want per-message channel selection with titles/captions, keep using the inline keyboard approach; it’s flexible and avoids forcing users to remember commands.
        •	For persistence and concurrency safety, replace the in-memory user_last_posts with a real datastore (Redis/DB), keyed by user_id.

⸻

If you’re on aiogram v2
        •	Replace Dispatcher() wiring and filters accordingly (from aiogram.dispatcher.filters import Regexp etc.).
        •	Callback data can be handled with @dp.callback_query_handler(lambda c: c.data.startswith("ch:")).
        •	Polling: executor.start_polling(dp, skip_updates=True).

⸻

Common pitfalls
        •	“Bad Request: CHAT_WRITE_FORBIDDEN” → the bot isn’t admin of the channel.
        •	Telegraph images not loading → Telegraph requires publicly accessible image URLs (no cookies/headers/auth).
        •	Very long Telegraph pages or too many nodes can fail; keep it reasonable or paginate.

⸻

If you want, paste your current “get links → build HTML” functions and I’ll slot them straight into this scaffold so it’s truly plug-and-play.



sudo systemctl daemon-reload
sudo systemctl enable tg-telegraph-bot
sudo systemctl start tg-telegraph-bot
sudo systemctl status tg-telegraph-bot
# Logs:
journalctl -u tg-telegraph-bot -f
"""

import asyncio
import logging
import re
from collections import defaultdict
from typing import cast

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, User
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telegraph import Telegraph

from grabber.core.bot.config import get_settings
from grabber.core.settings import TELEGRAPH_TOKEN
from grabber.core.sources.asianviralhub import get_sources_for_asianviralhub
from grabber.core.sources.asiaontop import get_sources_for_asiaontop
from grabber.core.sources.buondua import get_sources_for_buondua
from grabber.core.sources.celeb_cx import get_sources_for_celebcx
from grabber.core.sources.chunmomo import get_sources_for_chunmomo
from grabber.core.sources.common import get_sources_for_common
from grabber.core.sources.cosxuxi import get_sources_for_cosxuxi
from grabber.core.sources.ehentai import get_sources_for_ehentai
from grabber.core.sources.eporner import get_sources_for_eporner
from grabber.core.sources.erome import get_sources_for_erome
from grabber.core.sources.erome_tv import get_sources_for_erome_tv
from grabber.core.sources.erome_vip import get_sources_for_erome_vip
from grabber.core.sources.everia import get_sources_for_everia
from grabber.core.sources.fapachi import get_sources_for_fapachi
from grabber.core.sources.fapello import get_sources_for_fapello
from grabber.core.sources.fapello_pics import get_sources_for_fapello_pics
from grabber.core.sources.fapello_ru import get_sources_for_fapello_ru
from grabber.core.sources.fapello_su import get_sources_for_fapello_su
from grabber.core.sources.fapello_to import get_sources_for_fapello_to
from grabber.core.sources.fapexy import get_sources_for_fapexy
from grabber.core.sources.fapeza import get_sources_for_fapeza
from grabber.core.sources.fapodrop import get_sources_for_fapodrop
from grabber.core.sources.fapomania import get_sources_for_fapomania
from grabber.core.sources.faponic import get_sources_for_faponic
from grabber.core.sources.fuligirl import get_sources_for_fuligirl
from grabber.core.sources.graph import get_for_telegraph
from grabber.core.sources.hentai_club import get_sources_for_hentai_club
from grabber.core.sources.hotgirl2024 import get_sources_for_hotgirl2024
from grabber.core.sources.hotgirl_asia import get_sources_for_hotgirl_asia
from grabber.core.sources.hotgirl_china import get_sources_for_hotgirl_china
from grabber.core.sources.hotleaks import get_sources_for_hotleaks
from grabber.core.sources.jrants import get_sources_for_jrant
from grabber.core.sources.kemono import get_sources_for_kemono
from grabber.core.sources.khd import get_sources_for_4khd
from grabber.core.sources.kup import get_sources_for_4kup
from grabber.core.sources.leakedzone import get_sources_for_leakedzone
from grabber.core.sources.leakgallery import get_sources_for_leakgallery
from grabber.core.sources.lewdweb import get_sources_for_lewdweb
from grabber.core.sources.lovecos import get_sources_for_lovecos
from grabber.core.sources.masterfap import get_sources_for_masterfap
from grabber.core.sources.misskon import get_sources_for_misskon
from grabber.core.sources.mitaku import get_sources_for_mitaku
from grabber.core.sources.notion import get_sources_for_notion
from grabber.core.sources.nsfw247 import get_sources_for_nsfw24
from grabber.core.sources.nudecosplay import get_sources_for_nudecosplay
from grabber.core.sources.nudogram import get_sources_for_nudogram
from grabber.core.sources.nudostar import get_sources_for_nudostar
from grabber.core.sources.ouo import ouo_bypass
from grabber.core.sources.picazor import get_sources_for_picazor
from grabber.core.sources.picsclub import get_sources_for_picsclub
from grabber.core.sources.pixibb import get_sources_for_pixibb
from grabber.core.sources.rokuhentai import get_sources_for_rokuhentai
from grabber.core.sources.spacemiss import get_sources_for_spacemiss
from grabber.core.sources.sweetlicious import get_sources_for_sweetlicious
from grabber.core.sources.thefapnet import get_sources_for_the_fap_net
from grabber.core.sources.thefappening import get_sources_for_fappening
from grabber.core.sources.ugirls import get_sources_for_ugirls
from grabber.core.sources.xasiat import get_for_xasiat
from grabber.core.sources.xchina import get_sources_for_xchina
from grabber.core.sources.xiuren import get_sources_for_xiuren
from grabber.core.sources.xlust import get_sources_for_xlust
from grabber.core.sources.xmissy import get_sources_for_xmissy
from grabber.core.sources.xpics import get_sources_for_xpics
from grabber.core.utils import get_entity

# -----------------------------
# Setup
# -----------------------------
settings = get_settings()
bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
router = Router()
dp.include_router(router)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegraph client (one account per process is fine)
telegraph = Telegraph()
telegraph.create_account(
    short_name="bot",
    author_name=settings.telegraph_author_name or "AutoPoster",
    author_url=settings.telegraph_author_url or "",
)

# -----------------------------
# Helpers
# -----------------------------
URL_RE = re.compile(r"https?://\S+")


def extract_urls(text: str) -> list[str]:
    if not text:
        return []
    urls = URL_RE.findall(text)
    seen, uniq = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


# --- keyboard builder (FIXED) ---
def channels_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for channel_name, _ in settings.channels.items():
        kb.button(text=channel_name, callback_data=f"ch:{channel_name}")
    kb.adjust(2)
    return kb.as_markup()


# -----------------------------
# Your pipeline (await everything; no asyncio.run)
# -----------------------------
async def build_posts_and_send_to_channels(
    sources: list[str],
    channel: str,
    *,
    max_pages: int | None = None,
) -> None:
    getter_mapping = {
        "4kup.net": get_sources_for_4kup,
        "asianviralhub.com": get_sources_for_asianviralhub,
        "asigirl.com": get_sources_for_common,
        "bestgirlsexy.com": get_sources_for_common,
        "buondua.com": get_sources_for_buondua,
        "cosplaytele.com": get_sources_for_common,
        "cosxuxi.club": get_sources_for_cosxuxi,
        "dvir.ru": get_sources_for_nudogram,
        "e-hentai.org": get_sources_for_ehentai,
        "en.jrants.com": get_sources_for_jrant,
        "erome.com": get_sources_for_erome,
        "es.erome.com": get_sources_for_erome,
        "everia.club": get_sources_for_everia,
        "fapachi.com": get_sources_for_fapachi,
        "fapello.com": get_sources_for_fapello,
        "fapello.pics": get_sources_for_fapello_pics,
        "fapello.to": get_sources_for_fapello_to,
        "fapeza.com": get_sources_for_fapeza,
        "fapomania.com": get_sources_for_fapomania,
        "forum.lewdweb.net": get_sources_for_lewdweb,
        "fuligirl.top": get_sources_for_fuligirl,
        "hentaiclub.net": get_sources_for_hentai_club,
        "hotgirl.asia": get_sources_for_hotgirl_asia,
        "hotgirl.biz": get_sources_for_nudecosplay,
        "hotgirlchina.com": get_sources_for_hotgirl_china,
        "hotleaks.tv": get_sources_for_hotleaks,
        "jrants.com": get_sources_for_jrant,
        "kemono.cr": get_sources_for_kemono,
        "leakedzone.com": get_sources_for_leakedzone,
        "www.masterfap.net": get_sources_for_masterfap,
        "misskon.com": get_sources_for_misskon,
        "mitaku.net": get_sources_for_mitaku,
        "new.pixibb.com": get_sources_for_pixibb,
        "notion": get_sources_for_notion,
        "nsfw247.to": get_sources_for_nsfw24,
        "nudebird.biz": get_sources_for_nudecosplay,
        "nudecosplay.biz": get_sources_for_nudecosplay,
        "nudogram.com": get_sources_for_nudogram,
        "nudostar.tv": get_sources_for_nudostar,
        "ouo": ouo_bypass,
        "picazor.com": get_sources_for_picazor,
        "pt.jrants.com": get_sources_for_jrant,
        "sexy.pixibb.com": get_sources_for_pixibb,
        "spacemiss.com": get_sources_for_spacemiss,
        "telegra.ph": get_for_telegraph,
        "thefappening.plus": get_sources_for_fappening,
        "ugirls.pics": get_sources_for_ugirls,
        "www.4khd.com": get_sources_for_4khd,
        "www.erome.com": get_sources_for_erome,
        "www.everiaclub.com": get_sources_for_everia,
        "www.hentaiclub.net": get_sources_for_hentai_club,
        "www.hotgirl2024.com": get_sources_for_hotgirl2024,
        "www.lovecos.net": get_sources_for_lovecos,
        "www.sweetlicious.net": get_sources_for_sweetlicious,
        "www.xasiat.com": get_for_xasiat,
        "www.xpics.me": get_sources_for_xpics,
        "xiuren.biz": get_sources_for_xiuren,
        "xlust.org": get_sources_for_xlust,
        "xmissy.nl": get_sources_for_xmissy,
        "xpics.me": get_sources_for_xpics,
        "youwu.lol": get_sources_for_fuligirl,
        "fapodrop.com": get_sources_for_fapodrop,
        "www.eporner.com": get_sources_for_eporner,
        "fapello.su": get_sources_for_fapello_su,
        "erome.vip": get_sources_for_erome_vip,
        "www.erome.vip": get_sources_for_erome_vip,
        "leakgallery.com": get_sources_for_leakgallery,
        "picsclub.ru": get_sources_for_picsclub,
        "celeb.cx": get_sources_for_celebcx,
        "chunmomo.net": get_sources_for_chunmomo,
        "avjb.com": get_for_xasiat,
        "rokuhentai.com": get_sources_for_rokuhentai,
        "thefap.net": get_sources_for_the_fap_net,
        "fapello.ru": get_sources_for_fapello_ru,
        "www.fapello.ru": get_sources_for_fapello_ru,
        "www.erome.tv": get_sources_for_erome_tv,
        "asiaon.top": get_sources_for_asiaontop,
        "en.xchina.co": get_sources_for_xchina,
        "faponic.com": get_sources_for_faponic,
        "fapexy.com": get_sources_for_fapexy,
    }

    telegraph_client = Telegraph(access_token=TELEGRAPH_TOKEN)
    final_dest = ""
    publish = True
    is_tag = False
    limit = 0
    is_video_enabled = False
    max_pages = 500 if max_pages is None else max_pages

    # run each entity's getter
    for source_url in sources:
        source_entity: str = asyncio.run(get_entity([source_url]))
        getter_images = getter_mapping.get(source_entity, get_sources_for_common)
        await getter_images(  # <-- await (no asyncio.run)
            sources=[source_url],
            entity=source_entity,
            telegraph_client=telegraph_client,
            final_dest=final_dest,
            save_to_telegraph=publish,
            is_tag=is_tag,
            limit=limit,
            is_video_enabled=is_video_enabled,
            channel=channel,  # <-- the chosen channel goes here
            max_pages=max_pages,
        )


# -----------------------------
# State (per-user pending links)
# -----------------------------
# In production, replace with Redis/DB keyed by user_id (and maybe chat_id).
pending_links: dict[int, list[str]] = {}

# Ask-for-pages state per user
waiting_for_pages: set[int] = set()
pending_max_pages: dict[int, int] = {}


async def handle_links_flow(urls: list[str], channel: str, max_pages: int | None = None):
    await build_posts_and_send_to_channels(urls, channel, max_pages=max_pages)


# -----------------------------
# Handlers (Router)
# -----------------------------
@router.message(Command("start"))
async def start_cmd(message: Message):
    await message.reply(
        "Send me links (pages or direct image URLs). Then pick a channel and I'll post everything there."
    )


# /post behaves like sending links: it collects links then asks for a channel
@router.message(Command("post"))
async def post_cmd(message: Message):
    raw = (message.text or "").split(maxsplit=1)
    logger.info(f"Received /post command with raw text: {raw}")
    if len(raw) < 2:
        await message.reply("Usage: <code>/post &lt;links...&gt;</code>")
        return
    urls = extract_urls(raw[1])
    if not urls:
        await message.reply("I didn't find any links in your message.")
        return

    # accumulate links for this user (user may send multiple messages)
    user = cast(User, message.from_user)
    u = user.id
    existing = pending_links.get(u, [])
    existing.extend(urls)
    if not existing:
        existing = urls
    pending_links[u] = existing
    logger.info(f"User {user.id} queued {len(existing)} links: {existing}")

    # NEW: ask for pages first
    waiting_for_pages.add(u)
    await message.reply(f"Got {len(urls)} link(s). How many pages should I use? Send a number (e.g., 5) or type 'all'.")


# --- handler: awaiting page count ---
@router.message(F.text & F.text.regexp(r"^\s*(?:\d+|All|all|\*)\s*$"))
async def on_pages_input(message: Message):
    user = cast(User, message.from_user)
    u = user.id

    # Only handle if we're expecting a page count from this user
    if u not in waiting_for_pages:
        return

    txt = (message.text or "").strip().lower()
    pages = 8000 if txt.lower() in {"all", "*"} else int(txt)

    pending_max_pages[u] = pages
    waiting_for_pages.discard(u)
    await message.reply(
        f"Great — I'll use {pages} page(s). Now choose a channel to post:",
        reply_markup=channels_keyboard(),
    )
    return


# --- handler: user sends message with links ---
@router.message(F.text.func(lambda text: text and "http" in text))
async def on_text_with_links(message: Message):
    urls = extract_urls(message.text or "")

    if not urls:
        return

    user = cast(User, message.from_user)
    u = user.id
    existing = pending_links.get(u, [])
    existing.extend(urls)
    if not existing:
        logger.info(f"User {user.id} sent links: {urls}")
        existing = urls
    pending_links[u] = existing
    logger.info(f"User {user.id} queued {len(existing)} links: {existing}")

    waiting_for_pages.add(u)
    await message.reply(f"Got {len(urls)} link(s). How many pages should I use? Send a number (e.g., 5) or type 'all'.")


@router.callback_query(F.data.startswith("ch:"))
async def on_channel_choice(cb: CallbackQuery):
    # The button payload is "ch:{channel_id}" (set in channels_keyboard)
    payload = cb.data.split(":", 1)[1]

    # Resolve to a numeric channel id:
    # - If the payload is already an id (your keyboard uses id), use it.
    # - If you ever switch the keyboard to send a name, map it here.
    channel_id = None
    if payload in settings.channels.values():  # payload is an id (current behavior)
        channel_id = payload
        display_name = next((n for n, cid in settings.channels.items() if cid == payload), payload)
    elif payload in settings.channels:  # payload is a name (future-proof)
        display_name = payload
        channel_id = settings.channels[payload]
    else:
        display_name = payload  # fallback, should not happen

    if not channel_id:
        await cb.answer("Unknown channel.", show_alert=True)
        return

    # Fetch the queued URLs for this user (collected in on_text_with_links / /post)
    u = cb.from_user.id
    urls = pending_links.get(u)
    if not urls:
        await cb.answer("No links queued. Send links first.", show_alert=True)
        return

    await cb.answer("Posting…")
    try:
        max_pages = pending_max_pages.get(u)  # <-- add this
        await handle_links_flow(urls, channel_id, max_pages=max_pages)
    except Exception as e:
        await cb.message.edit_text(f"Failed to post to <b>{display_name}</b>.\n<code>{e}</code>")
        pending_links.pop(u, None)
        pending_max_pages.pop(u, None)
        waiting_for_pages.discard(u)
        # keep the pending links so user can retry
        return

    # Success → clear queue and confirm
    pending_links.pop(u, None)
    pending_max_pages.pop(u, None)
    waiting_for_pages.discard(u)
    await cb.message.edit_text(f"Posted {len(urls)} link(s) to {display_name} with {max_pages} pages.")
    await cb.answer("Done.", show_alert=True)


# --- bootstrapping ---
async def main():
    bot = Bot(token=settings.bot_token)
    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
