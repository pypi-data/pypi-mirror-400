import asyncio
from collections import defaultdict
from pathlib import Path
from typing import ClassVar

import nest_asyncio
from cement import Controller, ex
from telegraph import Telegraph

from grabber.core.settings import TELEGRAPH_TOKEN
from grabber.core.sources.asianviralhub import get_sources_for_asianviralhub
from grabber.core.sources.asiaontop import get_sources_for_asiaontop
from grabber.core.sources.buondua import get_sources_for_buondua
from grabber.core.sources.bypass import bypass_link, bypass_ouo
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
from grabber.core.sources.paster import retrieve_paster_contents
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
from grabber.core.utils import get_entity, query_mapping, upload_folders_to_telegraph

from ..core.version import get_version

VERSION_BANNER = f"""
A beautiful CLI utility to download images from the web! {get_version()}
"""


class Base(Controller):
    class Meta:
        label = "base"

        # text displayed at the top of --help output
        description = "A beautiful CLI utility to download images from the web"

        # text displayed at the bottom of --help output
        epilog = "Usage: grabber --entity 4khd --folder 4khd --publish --sources <list of links>"

        # controller level arguments. ex: 'test --version'
        arguments: ClassVar = [
            ### add a version banner
            (
                ["-s", "--sources"],
                {
                    "dest": "sources",
                    "type": str,
                    "help": "List of links",
                    "nargs": "+",
                },
            ),
            (
                ["-f", "--folder"],
                {
                    "dest": "folder",
                    "default": "",
                    "type": str,
                    "help": "Folder where to save",
                },
            ),
            (
                ["-l", "--limit"],
                {
                    "dest": "limit",
                    "type": int,
                    "help": "Limit the amount of posts retrieved (used altogether with --tag)",
                    "default": 0,
                },
            ),
            (
                ["-p", "--publish"],
                {
                    "dest": "publish",
                    "action": "store_true",
                    "help": "Publish page to telegraph",
                },
            ),
            (
                ["-u", "--upload"],
                {
                    "dest": "upload",
                    "action": "store_true",
                    "help": "Upload and publish folders to telegraph",
                },
            ),
            (
                ["-t", "--tag"],
                {
                    "dest": "is_tag",
                    "action": "store_true",
                    "help": "Indicates that the link(s) passed is a tag in which the posts are paginated",
                },
            ),
            (
                ["-b", "--bot"],
                {
                    "dest": "bot",
                    "action": "store_true",
                    "help": "Should the newly post be sent to telegram?",
                },
            ),
            (
                ["-v", "--version"],
                {
                    "action": "store_true",
                    "dest": "version",
                    "help": "Version of the lib",
                },
            ),
            (
                ["-a", "--show-all-entities"],
                {
                    "action": "store_true",
                    "dest": "show_all_entities",
                    "help": "Show all the websites supported",
                },
            ),
            (
                ["-bl", "--bypass-link"],
                {
                    "dest": "bypass_link",
                    "type": str,
                    "help": "Bypass a link and returns the final URL",
                    "default": "",
                    "nargs": "+",
                },
            ),
            (
                ["-vd", "--video-enabled"],
                {
                    "dest": "is_video_enabled",
                    "action": "store_true",
                    "help": "Indicates that should also try to grab videos",
                },
            ),
            (
                ["-c", "--channel"],
                {
                    "dest": "channel",
                    "type": str,
                    "help": "Optional channel to where posts will be sent to",
                },
            ),
            (
                ["-mp", "--max-pages"],
                {
                    "dest": "max_pages",
                    "type": int,
                    "help": "Limit the amount of pages when there's too much",
                    "default": 50,
                },
            ),
        ]

    @ex(hide=True)
    def _default(self):
        """Default action if no sub-command is passed."""
        nest_asyncio.apply()

        sources: list[str] = self.app.pargs.sources
        folder = self.app.pargs.folder

        if folder:
            final_dest = Path(folder)
        else:
            final_dest = folder
        publish = self.app.pargs.publish
        # publish = True
        upload = self.app.pargs.upload
        is_tag = self.app.pargs.is_tag
        limit = self.app.pargs.limit
        version = self.app.pargs.version
        send_to_telegram = self.app.pargs.bot
        send_to_telegram = True
        telegraph_client = Telegraph(access_token=TELEGRAPH_TOKEN)
        show_all_entities = self.app.pargs.show_all_entities
        links_to_bypass: list[str] = self.app.pargs.bypass_link
        is_video_enabled = self.app.pargs.is_video_enabled
        channel = self.app.pargs.channel
        max_pages = self.app.pargs.max_pages

        if links_to_bypass:
            entity = asyncio.run(get_entity(links_to_bypass))
            if entity == "ouo":
                asyncio.run(ouo_bypass(links_to_bypass))
            elif entity == "paster.so":
                paster_ids: list[str] = []
                for paster_link in links_to_bypass:
                    paster_id = paster_link.split("/")[-1]
                    paster_ids.append(paster_id)
                paster_contents = retrieve_paster_contents(paster_ids)

                for content in paster_contents:
                    print(f"{content}\n\n\n")
                return
            else:
                for link in links_to_bypass:
                    try:
                        final_url = bypass_link(link)
                    except Exception:
                        final_url = None

                    if final_url is None:
                        final_url = bypass_ouo(link)

                    print(f"{final_url}")
                return

        if show_all_entities:
            websites = "All websites supported:\n"
            entities = sorted(list(query_mapping.keys()))
            for entity in entities:
                websites += f"\t- {entity}\n"

            print(websites)
            return

        if version:
            print(VERSION_BANNER)
            return

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

        if upload:
            asyncio.run(
                upload_folders_to_telegraph(
                    folder_name=final_dest,
                    limit=limit,
                    send_to_channel=send_to_telegram,
                    telegraph_client=telegraph_client,
                )
            )
        else:
            for source_url in sources:
                source_entity: str = asyncio.run(get_entity([source_url]))
                getter_images = getter_mapping.get(source_entity, get_sources_for_common)
                asyncio.run(
                    getter_images(
                        sources=[source_url],
                        entity=source_entity,
                        telegraph_client=telegraph_client,
                        final_dest=final_dest,
                        save_to_telegraph=publish,
                        is_tag=is_tag,
                        limit=limit,
                        is_video_enabled=is_video_enabled,
                        channel=channel,
                        max_pages=max_pages,
                    )
                )
