import re
from urllib.parse import urlparse

import PyBypass as bypasser
from bs4 import BeautifulSoup
from curl_cffi import requests


def RecaptchaV3():
    import requests

    ANCHOR_URL = "https://www.google.com/recaptcha/api2/anchor?ar=1&k=6Lcr1ncUAAAAAH3cghg6cOTPGARa8adOf-y9zv2x&co=aHR0cHM6Ly9vdW8ucHJlc3M6NDQz&hl=en&v=pCoGBhjs9s8EhFOHJFe8cqis&size=invisible&cb=ahgyd1gkfkhe"
    url_base = "https://www.google.com/recaptcha/"
    post_data = "v={}&reason=q&c={}&k={}&co={}"
    client = requests.Session()
    client.headers.update({"content-type": "application/x-www-form-urlencoded"})
    matches = re.findall(r"([api2|enterprise]+)\/anchor\?(.*)", ANCHOR_URL)[0]
    url_base += matches[0] + "/"
    params = matches[1]
    res = client.get(url_base + "anchor", params=params)
    token = re.findall(r'"recaptcha-token" value="(.*?)"', res.text)[0]
    params = dict(pair.split("=") for pair in params.split("&"))
    post_data = post_data.format(params["v"], token, params["k"], params["co"])
    res = client.post(url_base + "reload", params=f"k={params['k']}", data=post_data)
    answer = re.findall(r'"rresp","(.*?)"', res.text)[0]
    return answer


def bypass_ouo(url: str) -> str:
    client = requests.Session()
    client.headers.update(
        {
            "authority": "ouo.io",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "referer": "http://www.google.com/ig/adde?moduleurl=",
            "upgrade-insecure-requests": "1",
        }
    )
    tempurl = url.replace("ouo.press", "ouo.io")
    p = urlparse(tempurl)
    id = tempurl.split("/")[-1]
    res = client.get(tempurl, impersonate="chrome110")
    next_url = f"{p.scheme}://{p.hostname}/go/{id}"

    for _ in range(2):
        if res.headers.get("Location"):
            break

        bs4 = BeautifulSoup(res.content, "lxml")
        inputs = bs4.findAll("input", {"name": re.compile(r"token$")})
        data = {input.get("name"): input.get("value") for input in inputs}
        data["x-token"] = RecaptchaV3()

        h = {"content-type": "application/x-www-form-urlencoded"}

        res = client.post(
            next_url,
            data=data,
            headers=h,
            allow_redirects=False,
            impersonate="chrome110",
        )
        next_url = f"{p.scheme}://{p.hostname}/xreallcygo/{id}"

    return res.headers.get("Location")


# st.set_page_config(
#     page_title="URL Bypasser",
#     page_icon="🧊",
#     layout="centered",
#     initial_sidebar_state="auto",
#     menu_items={
#         "Get Help": "https://telegram.me/ask_admin001",
#         "Report a bug": "https://telegram.me/ask_admin001",
#         "About": "This is URL Bypasser for ADLINKFLY based website. Made by [Kevin](https://github.com/kevinnadar22)",
#     },
# )
#
#
# def random_celeb():
#     return random.choice([st.balloons()])


# st.title("URL Bypasser")
# tab1, tab2 = st.tabs(
#     [
#         "Bypass",
#         "Available Websites",
#     ]
# )
#
# banned_websites = [
#     "linkvertise"
# ]

# __avl_website__ = [
#     "try2link.com",
#     " adf.ly",
#     " bit.ly",
#     " ouo.io",
#     " ouo.press",
#     " shareus.in",
#     " shortly.xyz",
#     " tinyurl.com",
#     " thinfi.com",
#     " hypershort.com ",
#     "safeurl.sirigan.my.id",
#     " gtlinks.me",
#     " loan.kinemaster.cc",
#     " theforyou.in",
#     " shorte.st",
#     " earn4link.in",
#     " tekcrypt.in",
#     " link.short2url.in",
#     " go.rocklinks.net",
#     " rocklinks.net",
#     " earn.moneykamalo.com",
#     " m.easysky.in",
#     " indianshortner.in",
#     " open.crazyblog.in",
#     " link.tnvalue.in",
#     " shortingly.me",
#     " open2get.in",
#     " dulink.in",
#     " bindaaslinks.com",
#     " za.uy",
#     " pdiskshortener.com",
#     " mdiskshortner.link",
#     " go.earnl.xyz",
#     " g.rewayatcafe.com",
#     " ser2.crazyblog.in",
#     " bitshorten.com",
#     " rocklink.in",
#     " droplink.co",
#     " tnlink.in",
#     " ez4short.com",
#     " xpshort.com",
#     " vearnl.in",
#     " adrinolinks.in",
#     " techymozo.com",
#     " linkbnao.com",
#     " linksxyz.in",
#     " short-jambo.com",
#     " ads.droplink.co.in",
#     " linkpays.in",
#     " pi-l.ink",
#     " link.tnlink.in ",
#     " pkin.me",
# ]


def bypass_link(url: str) -> str | None:
    bypassed_link: str | None = bypasser.bypass(url)
    return bypassed_link


# with tab1:
#     show_alert = False
#     url = st.text_input(label="Paste your URL")
#     if st.button("Submit"):
#         if url:
#             if any(banned in url for banned in banned_websites):
#                 st.error("This website is not supported")
#                 st.stop()
#             try:
#                 with st.spinner("Loading..."):
#                     bypassed_link = bypasser.bypass(url)
#                     st.success(bypassed_link)
#
#                 random_celeb()
#
#                 with st.expander("Copy"):
#                     st.code(bypassed_link)
#
#             except (
#                 UnableToBypassError,
#                 BypasserNotFoundError,
#                 UrlConnectionError,
#             ) as e:
#                 if show_alert := True:
#                     st.error(e)
#
#             if st.button("Dismiss"):
#                 show_alert = False
#
#         elif show_alert := True:
#             st.error("No URLS found")
#
# with tab2:
#     st.subheader("Available Websites")
#     st.table(__avl_website__)
