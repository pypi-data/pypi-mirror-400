https://cosplaytele.com/category/anime/page/2/
https://cosplaytele.com/ganyu-santa/
    soup.select('a[href^="https://cosplaytele.com/wp-content/uploads/"]')
    soup.select('a[href^="https://terabox.com"]')


------------------------------------------------------------------------------------------------------------


https://waifubitches.com/category/cosplay
    <a data-fancybox="gallery" data-sizes="(max-width: 2560px)" data-srcset="https://waifubitches.com/images/a/1280/-10000001/10003591/1.jpg 1280w" href="https://waifubitches.com/images/a/1280/-10000001/10003591/1.jpg" target="_blank">
    
    soup.select('[href^="/gallery/"][style="text-shadow:1px 1px #999"]')
    soup.select('[data-srcset^="https://waifubitches.com/images/a/1280/"][target^="_blank"]')


------------------------------------------------------------------------------------------------------------


https://bunkrr.ru/a/HQGkU6sB
https://bunkrr.ru/a/VdAplqXd
    After getting the content of 'href' we need to make another request using the path from that
    'href' as the new URL.
        soup.select('[href^="/i/"][target^="_blank"]')
        soup.select('[href^="/v/"][target^="_blank"]')
 
        '/i/🤤🤤🤤-glN3owGx.jpg'
    
    ```
    from bs4 import BeautifulSoup
    from requests_html import AsyncHTMLSession

    async def get_url(url, query):
        asession = AsyncHTMLSession()
        r = await asession.get(url)
        await r.html.arender()
        soup = BeautifulSoup(r.html.raw_html.decode())
        tag = soup.select(query)
        if not tag or len(tag) == 0:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError as e:
                if str(e).startswith('There is no current event loop in thread'):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    r.html.render()
                    soup = BeautifulSoup(r.html.raw_html.decode())
                    tag = soup.select(query)
        return r, tag

    url = 'https://bunkrr.ru/a/PkYk59vl'
    res, tags = await get_url(url, '[href^="/i/"][target^="_blank"]')
    final_links = []

    for tag in tags:
        final_links.append(tag.attrs['href'])


    for final_link in final_links:
        response = this_session.get(f'https://bunkrr.ru/{tags[4].attrs["href"]}')
        soup = BeautifulSoup(response.content)

        img_links = []
        for tag in soup4.select('[href^="https://i-milkshake.bunkr.ru"]'):
            img_links.append(tag.attrs['href'])
    ```

------------------------------------------------------------------------------------------------------------

https://jpg4.su/img/twm-paolino.YgwXlP6
    soup.select('[src^="https://simp4.jpg.church/Screenshot_"]')


------------------------------------------------------------------------------------------------------------


https://www.erome.com/a/4ZVuwVVE
    soup.findAll(lambda tag: tag if 'alt' in tag.attrs and not tag.attrs['alt'].startswith('erome') else None)


------------------------------------------------------------------------------------------------------------


https://cyberdrop.me/a/KWsljKkQ
    After getting the content of 'href' we need to make another request using the path from that
    'href' as the new URL.
    When accessing the src image link, it is still giving invalid URL error

    soup.select('[href^="/f/"][rel="noopener noreferrer"]')

    ```
    from bs4 import BeautifulSoup
    from requests_html import AsyncHTMLSession


    async def get_url():
        asession = AsyncHTMLSession()
        r = await asession.get('https://cyberdrop.me/f/ZOqodfC8qVSAEa')
        await r.html.arender()
        soup = BeautifulSoup(r.html.raw_html.decode())
        tag = soup.select('img[src^="https://sun.cyberdrop.ch/api/fc/"]')
        if not tag or len(tag) == 0:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError as e:
                if str(e).startswith('There is no current event loop in thread'):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    r.html.render()
                    soup = BeautifulSoup(r.html.raw_html.decode())
                    tag = soup.select('img[src^="https://sun.cyberdrop.ch/api/fc/"]')
        return r, tag
    ```


res, tag = await get_url()

------------------------------------------------------------------------------------------------------------

https://onlyfans-leaksr.blogspot.com/2023/08/peachjars_23.html



https://fun-cosplay.com/cosplay/84b0e9a4c13274cadab9b046467b8576/Nikumikyo-%E2%80%93-Katsushika-Hokusai
https://cosplaysgirlsbabes.wordpress.com/2019/08/05/high-school-of-dead-rias-gremory-by-lillybethrose/

https://sexboom.co/aon-supitsara/
    Needs VPN proxy in Thailand
------------------------------------------------------------------------------------------------------------

https://kawai.vip/tag/cosplay/
    https://kawai.vip/melandinha-me1adinha-tatsumaki-cosplay-pict/
    https://kawai.vip/hoshimachi-cosplay/
    https://kawai.vip/zhang-heyu/
    https://kawai.vip/xidaidai-kitagawa-marin-video/
    https://kawai.vip/kameaam-ai-version/

https://www.nekosaifree.site/search/label/Cosplay
    https://www.nekosaifree.site/2024/01/saizneko-christmas-is-coming.html?m=1
    https://www.nekosaifree.site/search/label/Big%20Size

https://chicascosplaystudio.com/hoshilily-pack-cosplay-yoel-doujin/
    https://chicascosplaystudio.com/imagenes-hoshilily-pack-cosplay-yoel-doujin/

https://chottie.net/blog/tag/cosplay

------------------------------------------------------------------------------------------------------------

DIRECT LINK TO DOWNLOAD
    https://www.8kcosplay.com/%e5%a4%8f%e9%b8%bd%e9%b8%bd%e4%b8%8d%e6%83%b3%e8%b5%b7%e5%ba%8a-no-25-%e7%ba%a6%e5%b0%94%e5%a4%aa%e5%a4%aa%e8%b4%b5%e5%a6%87%e5%86%85%e8%a1%a3-yor-forger-lingeries/

------------------------------------------------------------------------------------------------------------
https://www.kireicosplay.com/photoset/akane-araragi-norafawn-kobeni-makima-nurses/
http://mmcoser.com/21095.html
https://cospian.blogspot.com/member/499256
https://packsvids.com/shadory-pool-party-caitlyn

https://3dcosplay.blogspot.com/
    https://3dcosplay.blogspot.com/search/label/COSPLAY?&max-results=5

https://nucosplay.com/cosplay-models/

------------------------------------------------------------------------------------------------------------