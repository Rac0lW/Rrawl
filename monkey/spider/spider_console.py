import os
import time
import sys
sys.path.append('E://Project/Rrawl')
from importlib import import_module

from monkey.config.config import Config
from monkey.utils.log import logger

def file_name(file_dir=os.path.join(Config.BASE_DIR, "spider/sources")):
    """
    Get spider class
    :param file_dir:
    :return:
    """
    all_files = []
    for file in os.listdir(file_dir):
        if file.endswith("_spider.py"):
            all_files.append(file.replace(".py", ""))
    return all_files


def spider_console():
    # set the time that we want(s)
    run_time = 10
    start_time = time.time()


    start = time.time()
    all_files = file_name()
    while True:
        # count the time that has already passed
        elapsed_time = time.time() - start_time


        for spider in all_files:
            spider_module = import_module("monkey.spider.sources.{}".format(spider))
            if elapsed_time > run_time:
                break
            spider_module.main()
        
        break

    logger.info(f"Time costs: {time.time() - start}")


if __name__ == "__main__":
    spider_console()