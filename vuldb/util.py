# -*- encoding: utf8 -*-
import datetime
import fileinput as fi
import inspect
import logging
import os
import re
from urllib import unquote
import operator

import requests


def path(*paths):
    """

    :param paths:
    :return:
    """
    MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(MODULE_PATH, *paths)


def get_special_date(delta=0, format="%Y%m%d"):
    """
    now 20160918, default delata = 0
    :return:
    """
    date = (datetime.date.today() + datetime.timedelta(days=delta)).strftime(format)
    return date


def __getDataSourceName(memeber_name):
    """
    get online module name
    :param memeber_name:
    :return:
    """
    datasource_names = []
    modules = inspect.getmembers(memeber_name, inspect.ismodule)
    num_of_modules = len(modules)

    if num_of_modules != 0:
        for module in modules:
            class_name = module[0]

            datasource_names.append(class_name)
    return datasource_names


def url_santisfy(url):
    """
    check a url is evil or not
    http://blog.blindspotsecurity.com/2016/06/advisory-http-header-injection-in.html
    :param url:
    :return:
    """

    try:
        url_decode = unquote(url)
    except:
        return False

    if "%0d%0a" in url or "\r\n" in url_decode:
        return False
    else:
        return True
    return False


def count_record(fname):
    """
    return the number of records in a file
    :param fname:
    :return:
    """
    if not os.path.exists(fname):
        return 0
    for line in fi.input(fname):
        pass
    return fi.lineno()


def request_common(url=None, method=None, headers=None, auth=None, params=None, data=None,
                   json=None, timeout=10,
                   max_redirects=30):
    """

    :param url:
    :param method:
    :param headers:
    :param proxy:
    :param auth:
    :param params:
    :param data:
    :param timeout:
    :param debug:
    :return:
    """
    # check url is evil for python
    if not url_santisfy(url):
        return

    s = requests.session()
    s.max_redirects = max_redirects
    # setting headers
    if not headers:
        headers = {}

    headers[
        'User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 " \
                        "(KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"

    try:
        r = s.request(method, url, params=params, data=data, auth=auth, json=json, timeout=timeout)

        content = ">>>>>>>>> %s %s  detail >>>>>>>>\n" % (method, url)
        content = content + ">>>>request header: \n"
        content = content + repr(r.request.headers) + "\n"

        content = content + ">>>>response header: \n"
        content = content + repr(r.headers) + "\n"

        content = content + ">>>>response code: \n"
        content = content + repr(r.status_code) + "\n"

        content = content + ">>>>response content: \n"
        content = content + repr(r.content) + "\n"
        content = content + ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n"
        logging.debug(content)
        return r



    except Exception as e:
        content = "[REQUEST_FAILED]:%s %s failed : %s" % (method, url, repr(e))
        logging.error(content)
        return

    return


def getChineseChar(st):
    """
    get chinese char of a statement
    :param st:
    :return:
    """
    for l in re.findall(ur'[\u4e00-\u9fff]+', st):
        if l.find("漏洞") != -1:
            yield l


def sortByDictValue(dictob, reverse=False):
    """
    sort by dict value
    :param dictob:
    :param reverse:
    :return: [(K1,V1),(K2,V2),...,(Kn,Vn)
    """
    return sorted(dictob.items(), key=operator.itemgetter(1), reverse=reverse)


def isHitKeyword(st, keywordlist):
    """

    :param st: string  "逻辑漏洞"
    :param keywordlist: list   ["设计错误", "边界漏洞", "竞争条件"]
    :return:
    """
    for k in keywordlist:
        if st.find(k) != -1:
            return True
    return False
