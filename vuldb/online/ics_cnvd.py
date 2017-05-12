# -*- coding: utf-8 -*-
import logging

from bs4 import BeautifulSoup

import vuldb.util as util


class ICS_CNVD(object):
    def __init__(self, is_first_crawler=False,
                 timeout=10,
                 htmlparser="lxml",
                 source="ics.cnvd.org.cn",
                 base_url="http://ics.cnvd.org.cn"
                 ):
        self.is_first_crawler = is_first_crawler
        self.timeout = timeout
        self.htmlparser = htmlparser
        self.source = source
        self.base_url = base_url

    def getItemURL(self):
        """
        get page no
        :return: ('/?max=20&offset=1020', u'52')
        """
        r = util.request_common(url=self.base_url, method="GET")
        if r.status_code != 200:
            return (None, None)

        html = BeautifulSoup(r.content, self.htmlparser)

        page_detail = html.find("div", {'class': 'pages clearfix'})
        if page_detail:
            url_list = page_detail.find_all("a")
            if url_list and len(url_list) > 2:
                url_last = url_list[-2]
                url_last_href = url_last['href']
                url_last_text = url_last.get_text()
                return (url_last_href, url_last_text)

        return (None, None)

    def crawlItem(self, urlpath):
        """
        craw single page
        :param urlpath:
        :return:
        """
        url = "%s%s" % (self.base_url, urlpath)
        logging.info("[Crawerl]: %s" % url)

        r = util.request_common(url=url, method="GET")
        if r and r.status_code != 200:
            return

        html = BeautifulSoup(r.content, self.htmlparser)

        vuls = html.find("tbody", {'id': 'tr'})

        if vuls:
            vuls = vuls.find_all("tr")

            for item in vuls:
                vul_items = item.find_all("td")

                if vul_items and len(vul_items) > 4:
                    vul_url = vul_items[0].find("a")["href"].strip()
                    vul_title = vul_items[0].find("a")["title"].strip()

                    vul_date = vul_items[-1].get_text().strip()
                    vul_level = vul_items[-5].get_text().strip()

                    result = {
                        "vul_title": vul_title,
                        "vul_url": vul_url,
                        "vul_date": vul_date,
                        "vul_level": vul_level
                    }

                    yield result

    def crawler(self):

        if self.is_first_crawler is True:

            (urlpath, pageno) = self.getItemURL()
            if urlpath is None:
                return
            if pageno is None:
                return

            pageno = int(pageno)

            if pageno > 0:
                urlpath = urlpath[0:urlpath.find("offset=") + 7]
                step = urlpath[urlpath.find("=") + 1:urlpath.find("&")]
                step = int(step)
                if step > 0:
                    for x in range(0, pageno):

                        url = "%s%d" % (urlpath, x * step)
                        for result in self.crawlItem(url):
                            yield result
        else:
            for result in self.crawlItem(""):
                yield result


def crawlerVulDB(is_first_crawler=False):
    """
    crawler
    :param is_first_crawler:
    :return:
    """

    co = ICS_CNVD(is_first_crawler=is_first_crawler)
    for result in co.crawler():
        yield result


