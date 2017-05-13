# -*- encoding: utf8 -*-
import codecs



import logging

import attack_cat
import vuldb.util as util


import sys
default_encoding = 'utf-8'

if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


def statisticVulType(fname):
    """

    :param fname:
    :return: return: [(K1,V1),(K2,V2),...,(Kn,Vn)
    """
    # 1. sorted keyword
    keywrodstatistic = dict()
    with codecs.open(fname, mode='rb', encoding='utf-8') as fr:
        for l in fr:
            if l:
                for c in util.getChineseChar(l):

                    if keywrodstatistic.get(c) is None:
                        keywrodstatistic[c] = 1
                    else:
                        keywrodstatistic[c] = keywrodstatistic[c] + 1
    keywrodstatistic = util.sortByDictValue(keywrodstatistic, reverse=True)

    # cat vultype
    result = {}
    for keyword, num in keywrodstatistic:
        ishitvultype = False
        for vultype, keywordlist in attack_cat.attack_cat.items():
            ishitkeywordlist = util.isHitKeyword(keyword, keywordlist)
            if ishitkeywordlist:
                result[vultype] = result.get(vultype, 0) + num
                ishitvultype = True
                break
        if ishitvultype is False:
            other = "其他漏洞"
            logging.info("[other]:%s\t%d" %(keyword,num))
            result[other] = result.get(other, 0) + num

    result = util.sortByDictValue(result, reverse=True)

    return result


if __name__ == "__main__":
    result = statisticVulType(util.path("data/vuldb.txt"))
    for k, v in result:
        print "%s\t%s" % (k, v)
