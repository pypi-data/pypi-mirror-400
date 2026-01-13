import multiprocessing

DEFAULT_THREADS_NUMBER = multiprocessing.cpu_count()
PAGINATION_QUERY = "div.jeg_navigation.jeg_pagination"
PAGINATION_PAGES_COUNT_QUERY = f"{PAGINATION_QUERY} span.page_info"
PAGINATION_BASE_URL_QUERY = "div.jeg_navigation.jeg_pagination a.page_number"
POSTS_QUERY_XPATH = (
    "/html/body/div[2]/div[5]/div/div[1]/div/div/div[2]/div/div/div[2]/div/div[1]/div/div/div/article/div/div/a"
)
READ_TIMEOUT_SECONDS = 25
CONNECT_TIMEOUT_SECONDS = 15
DEFAULT_PER_IMAGE_CONCURRENCY = 10
PER_HOST_LIMIT = 6
CONNECT_TIMEOUT_S = 30
READ_TIMEOUT_S = 60
PER_IMAGE_HARD_TIMEOUT_S = 120

query_mapping = {
    "xiuren.biz": ("div.content-inner img", "src"),
    "nudebird.biz": ("div.thecontent a", "href"),
    "hotgirl.biz": ("div.thecontent a", "href"),
    "nudecosplay.biz": ("div.content-inner a img", "src"),
    "www.v2ph.com": (
        "div.photos-list.text-center img",
        "src",
    ),  # Needs to handle pagination
    "cgcosplay.org": ("div.gallery-icon.portrait img", "src"),
    "mitaku.net": ("div.msacwl-img-wrap img", "src"),
    "www.xasiat.com": ("div.images a", "href"),
    "avjb.com": ("div.images a img", "data-original"),
    "telegra.ph": ("img", "src"),
    "www.4khd.com": (
        "div.is-layout-constrained.entry-content.wp-block-post-content img",
        "src",
    ),
    "yellow": (
        "div.elementor-widget-container a[href^='https://terabox.com']",
        "href",
    ),
    "everia.club": ("div.divone div.mainleft img", "data-original"),
    "www.everiaclub.com": ("div.divone div.mainleft img", "src"),
    "bestgirlsexy.com": ("div.elementor-widget-container p img", "src"),
    "asigirl.com": ("a.asigirl-item", "href"),
    "cosplaytele.com": ("img.attachment-full.size-full", "src"),
    "hotgirl.asia": ("div.galeria_img img", "src"),
    "4kup.net": ("div#gallery div.caption a.cp", "href"),
    "buondua.com": ("div.article-fulltext p img", "src"),
    "www.erome.com": (
        "div.col-sm-12.page-content div div.media-group div.img div.img-blur img",
        "data-src",
    ),
    "erome.com": (
        "div.col-sm-12.page-content div div.media-group div.img div.img-blur img",
        "data-src",
    ),
    "es.erome.com": (
        "div.col-sm-12.page-content div div.media-group div.img div.img-blur img",
        "data-src",
    ),
    "notion": (
        "div.notion-page-content > div > div > div > div > div > div.notion-cursor-default > div > div > div > img",
        "src",
    ),
    "new.pixibb.com": (
        "div.blog-post-wrap > article.post-details > div.entry-content img",
        "src",
    ),
    "sexy.pixibb.com": (
        "div.blog-post-wrap > article.post-details > div.entry-content img",
        "src",
    ),
    "spacemiss.com": ("div.tdb-block-inner.td-fix-index > img", "src"),
    "www.hentaiclub.net": (
        "div.content div.post.row img.post-item-img.lazy",
        "data-original",
    ),
    "ugirls.pics": ("div#main div.my-2 img", "src"),
    "xlust.org": (
        "div.entry-wrapper div.entry-content.u-clearfix div.rl-gallery-container a",
        "href",
    ),
    "bikiniz.net": ("div.image_div img", "src"),
    "hotgirlchina.com": ("div.entry-inner p img", "src"),
    "cup2d.com": (
        "div.gridshow-posts-wrapper > article div.entry-content.gridshow-clearfix a",
        "href",
    ),
    "en.taotu.org": ("div#content div#MainContent_piclist.piclist a", "href"),
    "pt.jrants.com": ("div.bialty-container p img", "src"),
    "jrants.com": ("div.entry-content p img", "src"),
    "en.jrants.com": ("div.entry-content p img", "src"),
    "misskon.com": ("article div.entry p img", "data-src"),
    "www.nncos.com": ("div.entry-content div.entry.themeform p img", "data-src"),
    "www.lovecos.net": ("div.img p a img", "src"),
    "e-hentai.org": ("div#i3 img", "src"),
    "fuligirl.top": ("div.my-1 img", "src"),
    "youwu.lol": ("div.my-2 img", "src"),
    "cosxuxi.club": ("div.contentme a img", "src"),
    "www.hotgirl2024.com": (
        "div.article__content ul.article__image-list li.article__image-item a img",
        "data-src",
    ),
    "www.tokyobombers.com": (
        "div.gallery figure.gallery-item div.gallery-icon.portrait a img",
        "src",
    ),
    "tokyocafe.org": ("div.gallery figure.gallery-item div.gallery-icon.portrait a img", "src"),
    "forum.lewdweb.net": (
        "section.message-attachments ul.attachmentList li.file.file--linked a.file-preview",
        "href",
    ),
    "nudecosplaygirls.com": ("div#content article div.entry-inner div img", "src"),
    "vazounudes.com": ("div#content article div.entry-inner div img", "data-src"),
    "sheeshfans.com": ("div.block-album div.album-holder div.images a", "href"),
    "nsfw247.to": ("source", "src"),
    "asianviralhub.com": ("div.fp-player video", "src"),
    "www.sweetlicious.net": ("div.article__entry.entry-content div.wp-video video source", "src"),
    "happy.5ge.net": ("article p section img.image.lazyload", "data-src"),
    "sexygirl.cc": ("div.row.justify-content-center.m-1 div.row.mt-2 img", "src"),
    "xiunice.com": ("div.tdb-block-inner.td-fix-index figure img", "src"),
    "imgcup.com": ("div.post-entry div.inner-post-entry.entry-content figure img", "data-src"),
    "nudogram.com": ("div.content div.block-video div.video-holder div.player div.player-holder a img", "src"),
    "dvir.ru": ("div.content div.block-video div.video-holder div.player div.player-holder a img", "src"),
    "fapello.com": ("div a div.max-w-full img", "src"),
    "fapeza.com": ("div.image-row div.flex-1 a img", "src"),
    "kemono.cr": ("div.post__files div.post__thumbnail figure a", "href"),
    "fapachi.com": ("div.container div.row div.col-6.col-md-4.my-2.model-media-prew a img", "data-src"),
    "nudostar.tv": ("div.box div.list-videos div#list_videos_common_videos_list_items div.item a div.img img", "src"),
    "thefappening.plus": ("div.gallery figure.gallery__item a img.gallery_thumb", "src"),
    "fapomania.com": ("div.leftocontar div.previzakosblo div.previzako a div.previzakoimag img", "src"),
    "fapello.pics": ("div.site-content div.content-area main.site-main article a[rel='screenshot']", "href"),
    "www.masterfap.net": ("div#content div a div img", "src"),
    "fapello.to": ("", ""),
    "allasiangirls.net": ("div.article-inner div.entry-content div.separator a", "href"),
    "fapodrop.com": ("div.row div.one-pack a img", "src"),
    "www.eporner.com": ("div#container div.mbphoto2 a img", "src"),
    "fapello.su": ("a div.max-w-full img", "data-src"),
    "erome.vip": ("div.container div.grid figure a img", "src"),
    "www.erome.vip": ("div.container div.grid figure a img", "src"),
    "picsclub.ru": (
        "div.content-width div div.pad-content-listing div.list-item div.list-item-image a img",
        "data-src",
    ),
    "chunmomo.net": ("div[itemprop='articleBody'] p img", "src"),
    "rokuhentai.com": ("a.site-popunder-ad-slot", "href"),
    "thefap.net": ("a div.max-w-full img", "src"),
    "fapello.ru": ("div.grid-view figure.gallery-item a img.gallery-img", "src"),
    "www.erome.tv": ("div.album-inner.images a", "href"),
    "erome.tv": ("div.album-inner.images a", "href"),
    "en.xchina.co": ("div.list.photo-items div.item.photo-image a div", "style"),
    "faponic.com": ("div.photo-item img", "src"),
    "fapexy.com": ("a img", "src"),
}

headers_mapping = {
    "nudebird.biz": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "nudecosplay.biz": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "www.v2ph.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "cgcosplay.org": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "mitaku.net": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "www.xasiat.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "avjb.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "www.4khd.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "buondua.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    },
    "bunkr": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    },
    "bestgirlsexy.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "new.pixibb.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "sexy.pixibb.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "spacemiss.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "www.hentaiclub.net": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "ugirls.pics": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "xlust.org": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "common": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "bikiniz.net": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "hotgirlchina.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "cup2d.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "en.taotu.org": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "misskon.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "www.nncos.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "www.lovecos.net": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "e-hentai.org": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://e-hentai.org/",
    },
    "fuligirl.top": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "cosxuxi.club": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "forum.lewdweb.net": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "happy.5ge.net": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "www.xpics.me": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "xpics.me": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "fapomania.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "fapello.to": {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    },
    "hotleaks.tv": {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    },
    "leakedzone.com": {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    },
    "picazor.com": {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    },
    "fapello.su": {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    },
    "erome.vip": {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    },
    "www.erome.vip": {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    },
    "chunmomo.net": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    },
    "thefap.net": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    },
    "fapello.ru": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    },
    "www.erome.tv": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    },
    "erome.tv": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    },
    "en.xchina.co": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "faponic.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "fapexy.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
}


CHUNK_MAPPING = {
    99: 45,
    100: 50,
    150: 60,
    200: 70,
    250: 80,
    300: 90,
}
