import time
import threading
import traceback

from inspect import isgenerator
from typing import Callable, Type
from requests import RequestException

from cobweb.crawlers import Crawler
from cobweb.utils import check_pause
from cobweb.log_dots import LoghubDot
from cobweb.constant import DealModel, LogTemplate
from cobweb.base import Seed, Status, TaskQueue, BaseItem, Request, Response, logger


class Distributor(threading.Thread):

    def __init__(
            self,
            task: str,
            project: str,
            task_queue: TaskQueue,
            stop: threading.Event,
            pause: threading.Event,
            callback_register: Callable,
            SpiderCrawler: Type[Crawler]
    ):
        super().__init__()
        self.task = task
        self.project = project
        self.pause = pause

        self.task_queue = task_queue

        self.callback_register = callback_register
        self.Crawler = SpiderCrawler

        from cobweb import setting
        self.time_sleep = setting.SPIDER_TIME_SLEEP
        self.thread_num = setting.SPIDER_THREAD_NUM
        self.max_retries = setting.SPIDER_MAX_RETRIES
        self.loghub_dot = LoghubDot(stop=stop, project=self.project, task=self.task)

        logger.debug(f"Distribute instance attrs: {self.__dict__}")

    def distribute(self, task_id, item, status: Status):
        if isinstance(item, Request):
            item.seed.params.request_time = time.time()
            self.loghub_dot._build_request_log(item)
            self.process(task_id=task_id, item=item, callback=self.Crawler.download, status=Status.PROCESSING)

        elif isinstance(item, Response):
            if status == Status.FINISHED:
                raise TypeError("parse function can't yield a Response instance")
            item.seed.params.download_time = time.time()
            logger.debug(LogTemplate.download_info.format(
                detail=LogTemplate.log_info(item.seed.to_dict),
                retry=item.seed.params.retry,
                priority=item.seed.params.priority,
                seed_version=item.seed.params.seed_version,
                identifier=item.seed.identifier or "",
                status=item.response,
                response=LogTemplate.log_info(item.to_dict)
            ))
            self.loghub_dot._build_download_log(item)
            self.process(task_id=task_id, item=item, callback=self.Crawler.parse, status=Status.FINISHED)

        elif isinstance(item, BaseItem):
            item.seed.params.parse_time = time.time()
            self.loghub_dot._build_parse_log(item)
            self.task_queue.add_task(data=item, status=Status.UPLOAD, parent_id=task_id)

        elif isinstance(item, Seed):
            # todo: 新种子日志
            item.params.insert_time = time.time()
            self.task_queue.add_task(
                task_id=item.sid, data=item, status=Status.INSERT,
                priority=item.params.priority, parent_id=task_id
            )

        elif isinstance(item, str) and item != DealModel.done:
            raise TypeError("yield value type error!")

    def process(self, task_id, item, callback, status: Status):
        iterators = callback(item)
        if not isgenerator(iterators):
            raise TypeError(f"{callback.__name__} function isn't a generator!")
        for it in iterators:
            self.distribute(task_id=task_id, item=it, status=status)

    @check_pause
    def spider(self):
        if task_item := self.task_queue.get_pending_task():
            finsh_status = True
            seed = task_item.data
            status = Status.FINISHED
            task_id = task_item.task_id
            seed.params.start_time = time.time()

            if seed.params.retry and isinstance(seed.params.retry, int):
                time.sleep(self.time_sleep * seed.params.retry / 100)

            try:
                self.process(task_id=task_id, item=seed, callback=self.Crawler.request, status=Status.PENDING)
            except Exception as e:
                seed.params.retry += 1
                seed.params.failed_time = time.time()
                msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                if not seed.params.msg:
                    seed.params.traceback = [msg]
                elif isinstance(seed.params.msg, list):
                    seed.params.traceback.append(msg)

                if isinstance(e, RequestException):
                    self.loghub_dot._build_http_error_log(seed, e)
                else:
                    self.loghub_dot._build_exception_log(seed, e)

                if seed.params.retry < self.max_retries:
                    status = Status.PENDING
                    finsh_status = False

                logger.info(LogTemplate.download_exception.format(
                    detail=LogTemplate.log_info(seed.to_dict),
                    retry=seed.params.retry,
                    priority=seed.params.priority,
                    seed_version=seed.params.seed_version,
                    identifier=seed.identifier or "",
                    exception=msg
                ))

            finally:
                if finsh_status:
                    seed.params.finsh_time = time.time()
                    self.loghub_dot._build_finish_log(seed, status=bool(seed.params.retry < self.max_retries))
                self.task_queue.update_task(task_id, status=status, data=seed)

    def run(self):
        self.callback_register(self.loghub_dot._build_run, tag="LoghubDot")
        for _ in range(self.thread_num):
            self.callback_register(self.spider, tag="Distributor")
