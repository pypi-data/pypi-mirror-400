import logging
import requests


def url2html(session: requests.Session, url: str, **kwargs) -> str:
    """
    Usage::

        print(url2html(requests.Session(), 'https://www.baidu.com'))

    :param timeout: default = 30
    :param anti_cloudflare: default = False
    """
    timeout = kwargs["timeout"] if "timeout" in kwargs else 30
    anti_cloudflare = (
        kwargs["anti_cloudflare"] if "anti_cloudflare" in kwargs else False
    )
    logger: logging.Logger = kwargs["logger"] if "logger" in kwargs else logging

    result = ""

    try:
        resp = session.get(url, timeout=timeout)
        # requests 内部自动 处理了
        # if resp.headers.get("content-encoding") == "gzip":
        #     import gzip

        #     try:
        #         content = gzip.decompress(resp.content)
        #     except Exception:
        #         content = resp.content
        # elif resp.headers.get("content-encoding") == "br":
        #     import brotli

        #     try:
        #         content = brotli.decompress(resp.content)
        #     except brotli.error:
        #         content = resp.content
        # elif resp.headers.get("content-encoding") == "deflate":
        #     import zlib

        #     try:
        #         content = zlib.decompress(resp.content, -zlib.MAX_WBITS)
        #     except zlib.error:
        #         content = resp.content
        # else:
        #     content = resp.content
        content = resp.content
        result = content.decode("utf-8")

        # <!DOCTYPE html><html lang="en-US"><head><title>Just a moment...</title><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=Edge"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><link href="/cdn-cgi/styles/challenges.css" rel="stylesheet"></head><body class="no-js"><div class="main-wrapper" role="main"><div class="main-content"><noscript><div id="challenge-error-title"><div class="h2"><span class="icon-wrapper"><div class="heading-icon warning-icon"></div></span><span id="challenge-error-text">Enable JavaScript and cookies to continue</span></div></div></noscript></div></div>
        if (
            "<title>Just a moment...</title>" in result and anti_cloudflare
        ):  # cloudflare 反爬虫
            # cloudflare anti-bot
            # https://github.com/Anorov/cloudflare-scrape/commit/e510962c608382bcef5de75033d60cc98cb9561d
            # 也是基于requests的所以 设置环境变量proxy即可
            import toolkit_cmm.thirdparty.cloudflarescrape as cfscrape

            scraper = cfscrape.create_scraper(sess=session, delay=10)
            r = scraper.get(url)
            if r.status_code == 200:
                return str(r.content)
            else:
                logger.error(f"Response {r.status_code}")
                return str(r.content)
        else:
            return result
    except Exception as e:  # Timeout
        logger.exception(e)
        return ""
    return result


def html2soup(html):
    from bs4 import BeautifulSoup

    return BeautifulSoup(html, "lxml")


def url2soup(session: requests.Session, url: str, **kwargs):
    return html2soup(url2html(session=session, url=url, **kwargs))
