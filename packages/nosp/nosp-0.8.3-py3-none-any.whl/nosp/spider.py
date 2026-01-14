import abc
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from loguru import logger

from . import SpiderInfo
from .http import Request, BaseRequest
import argparse


class SpiderThreadPool(object):

    def __init__(self):
        self.executor: Optional[ThreadPoolExecutor] = None

    def future_callback(self, future):
        if future.exception():
            raise future.exception()

    def submit_task(self, task_func, task):
        """
        向线程池中添加新任务
        :param task_func:
        :param task:
        :return:
        """
        future = self.executor.submit(task_func, task)
        future.add_done_callback(self.future_callback)

    def get_task_count(self) -> int:
        """
        获取当前线程池中还有多少任务数量
        :return:
        """
        return self.executor._work_queue.qsize()

    def start_batch_task(self, task_func, task_list: list, thread_num: int, wait=True):
        """
        多线程批量处理任务
        :param task_func: 任务函数
        :param task_list: 任务列表
        :param thread_num: 线程数量
        :param wait: 是否等待
        :return:
        """
        self.executor = ThreadPoolExecutor(max_workers=thread_num)
        try:
            for task in task_list:
                future = self.executor.submit(task_func, *task)
                future.add_done_callback(self.future_callback)
        finally:
            if wait:
                self.executor.shutdown(wait=True)
            # if wait:
            #     self.executor.shutdown(wait=False)
            #     while True:
            #         try:
            #             time.sleep(10)
            #         except KeyboardInterrupt:
            #             self.executor.shutdown(wait=True,cancel_futures=True)

    def task_wait(self):
        self.executor.shutdown(wait=True)


class BaseSpider(abc.ABC):

    def __init__(self, info: SpiderInfo = None, headers=None, cookies=None, proxy_url=None):
        """
        Spider 基类
        :param info: SpiderInfo
        :param headers: self.request -> headers
        :param cookies: self.request -> cookies
        :param proxy_url: 代理池地址
        """
        self.info = info
        self.local = threading.local()
        self.headers = headers if headers is not None else getattr(self.__class__, "headers", None)
        self.cookies = cookies if cookies is not None else getattr(self.__class__, "cookies", None)
        self.proxy_url = proxy_url if proxy_url is not None else getattr(self.__class__, "proxy_url", None)

    def get_request(self):
        return Request(proxy_url=self.proxy_url, headers=self.headers, cookies=self.cookies)

    @property
    def request(self) -> BaseRequest:
        if not hasattr(self.local, 'request'):
            self.local.request = self.get_request()
        return self.local.request

    def start_cl(self, *args, **kwargs):
        pass

    def start(self, *args):
        parser = argparse.ArgumentParser()
        parser.add_argument("-cl", action="store_true",help="启用存量模式")
        parser.add_argument("-t", type=int, default=10, help="线程数量")
        parsed_args = parser.parse_args()  # 使用传入的 args，避免覆盖 sys.argv

        # 如果命令行没指定 -cl，则检查环境变量
        if not parsed_args.cl:
            cl_env = os.getenv('CL', '').lower()
            if cl_env in ('true', '1', 'yes', 'on'):
                parsed_args.cl = True

        if parsed_args.cl:
            logger.warning('cl=True')
            self.start_cl(thread_num=parsed_args.t)
            sys.exit(0)

    def page_list(self, *args):
        pass

    def page_detail(self, *args):
        pass

    def parse(self, *args):
        pass
