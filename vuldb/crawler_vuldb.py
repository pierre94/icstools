# -*- coding: utf-8 -*-
import os
import codecs
import datetime
import logging
from Queue import Queue
from threading import Thread

import vuldb.online as online
import vuldb.util as util
from vuldb.online import *


def crawlerVuldb(outputfile="", thread_num=20, is_first_crawler=False):
    """
    crawler vuldb
    :param outputfile:
    :param thread_num:
    :param is_first_crawler:
    :param is_debug:
    :return: num of records
    """

    def getData(i, q, fin):
        while True:
            datasource = q.get()

            datasourceclass = eval(datasource)

            for item in datasourceclass.crawlerVulDB(is_first_crawler=is_first_crawler):
                item = "%s\t%s\t%s\t%s" %(item.get("vul_date"),
                                               item.get("vul_level"),
                                               item.get("vul_url"),
                                               item.get("vul_title"))
                fin.write("%s%s" % (item, os.linesep))
            q.task_done()

    datasource_names = util.__getDataSourceName(online)

    num_of_datasource = len(datasource_names)

    if thread_num > num_of_datasource:
        thread_num = num_of_datasource

    start_time = datetime.datetime.now()
    with codecs.open(outputfile, mode='wb', encoding='utf-8',
                     errors='ignore') as fin:

        scrape_queue = Queue()
        for i in range(thread_num):
            worker = Thread(target=getData, args=(i, scrape_queue, fin))
            worker.setDaemon(True)
            worker.start()

        for source in datasource_names:
            scrape_queue.put(source)

        scrape_queue.join()

    end_time = datetime.datetime.now()
    collaspe = (end_time - start_time).seconds
    num_of_records = util.count_record(outputfile)

    logging.info("[CRAWLER_RESULT]: crawl %s "
                 "using %d seconds with %d threads "
                 "(first_crawler: %s) "
                 "and get %d records"
                 % (datasource_names,
                    collaspe, thread_num,
                    is_first_crawler,

                    num_of_records

                    ))
    return num_of_records


if __name__ == "__main__":
    import logger

    logger.generate_special_logger(level=logging.INFO,
                                   logtype="crawlervuldb",
                                   curdir="./log")

    thread_num = 10
    is_first_crawler = True
    outputfile = util.path("data/%s.txt" % util.get_special_date())
    crawlerVuldb(thread_num=thread_num, is_first_crawler=is_first_crawler,
                 outputfile=outputfile)
