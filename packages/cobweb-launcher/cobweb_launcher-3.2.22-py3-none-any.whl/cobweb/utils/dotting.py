import os
import json
import time
from threading import Event
from requests import RequestException, Response as requests_Response

from cobweb.base import Queue, Request, Seed, Response, BaseItem, logger
from aliyun.log import LogClient, LogItem, PutLogsRequest


class LoghubDot:

    def __init__(self, stop: Event, project: str, task: str) -> None:
        self._stop = stop
        self._queue = Queue()
        self._client = LogClient(
            endpoint=os.getenv("LOGHUB_ENDPOINT"),
            accessKeyId=os.getenv("LOGHUB_ACCESS_KEY"),
            accessKey=os.getenv("LOGHUB_SECRET_KEY")
        )
        self.project = project
        self.task = task

    def logging(self, topic, msg):
        log_item = LogItem()
        log_data = {
            "stage": topic,
            "message": msg,
            "project": self.project,
            "task": self.task,
        }

        for key, value in log_data.items():
            if not isinstance(value, str):
                log_data[key] = json.dumps(value, ensure_ascii=False)
            else:
                log_data[key] = value

        contents = sorted(log_data.items())
        log_item.set_contents(contents)
        self._queue.push(log_item)

    def _build_request_log(self, request_item: Request):
        log_item = LogItem()

        seed: Seed = request_item.seed
        get_time = seed.params.get_time
        start_time = seed.params.start_time
        request_time = seed.params.request_time
        stage_cost = request_time - start_time
        cost = request_time - start_time

        request_settings = json.dumps(
            request_item.request_settings,
            ensure_ascii=False, separators=(',', ':')
        )

        log_data = {
            "stage": "request",
            "project": self.project,
            "task": self.task,
            "seed": seed.to_string,
            "request": repr(request_item),
            "request_settings": request_settings,
            "get_time": get_time,
            "start_time": start_time,
            "stage_cost": stage_cost,
            "cost": cost,
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(request_time)),
        }

        for key, value in log_data.items():
            if not isinstance(value, str):
                log_data[key] = json.dumps(value, ensure_ascii=False)
            else:
                log_data[key] = value

        contents = sorted(log_data.items())
        log_item.set_contents(contents)
        self._queue.push(log_item)

    def _build_download_log(self, response_item: Response):
        """
        构建下载阶段的日志项

        Args:
            response_item: 响应对象
        """
        log_item = LogItem()

        seed: Seed = response_item.seed
        get_time = seed.params.get_time
        start_time = seed.params.start_time
        request_time = seed.params.request_time
        download_time = seed.params.download_time
        stage_cost = download_time - request_time
        cost = download_time - start_time

        log_data = {
            "stage": "download",
            "project": self.project,
            "task": self.task,
            "seed": seed.to_string,
            "response": repr(response_item),
            "get_time": get_time,
            "start_time": start_time,
            "request_time": request_time,
            "download_time": download_time,
            "stage_cost": stage_cost,
            "cost": cost,
            "proxy": seed.params.proxy or '-',
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(download_time)),
        }

        response = response_item.response
        if isinstance(response, requests_Response):
            log_data['request_info'] = {
                'method': response.request.method,
                'url': response.request.url,
                'headers': dict(response.request.headers),
                'body': response.request.body or "-",
            }
            log_data['response_info'] = {
                "status_code": response.status_code,
                "reason": response.reason,
                "headers": dict(response.headers),
                "content": response.text[:500],  # 截取内容
                "content_type": response.headers.get('content-type', '-'),
                "content_length": response.headers.get('content-length', '-'),
                "server": response.headers.get('server', '-'),
                "date": response.headers.get('date', '-'),
            }

        for key, value in log_data.items():
            if not isinstance(value, str):
                log_data[key] = json.dumps(value, ensure_ascii=False)
            else:
                log_data[key] = value

        contents = sorted(log_data.items())
        log_item.set_contents(contents)
        self._queue.push(log_item)

    def _build_parse_log(self, parse_item: BaseItem):
        log_item = LogItem()

        seed: Seed = parse_item.seed
        get_time = seed.params.get_time
        start_time = seed.params.start_time
        request_time = seed.params.request_time
        response_time = seed.params.response_time
        parse_time = seed.params.parse_time

        pre_time = request_time or response_time
        stage_cost = parse_time - pre_time
        cost = parse_time - start_time

        log_data = {
            "stage": "parse",
            "project": self.project,
            "task": self.task,
            "seed": seed.to_string,
            "parse": repr(parse_item),
            "get_time": get_time,
            "start_time": start_time,
            "parse_time": parse_time,
            "stage_cost": stage_cost,
            "cost": cost,
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(parse_time)),
        }

        for key, value in log_data.items():
            if not isinstance(value, str):
                log_data[key] = json.dumps(value, ensure_ascii=False)
            else:
                log_data[key] = value

        contents = sorted(log_data.items())
        log_item.set_contents(contents)
        self._queue.push(log_item)

    def _build_http_error_log(self, seed: Seed, e: RequestException):
        log_item = LogItem()

        status_code = getattr(e.response, 'status_code', '-')

        request_info = {
            'method': getattr(e.request, 'method', '-'),
            'url': getattr(e.request, 'url', '-'),
            'headers': dict(getattr(e.request, 'headers', {})),
            'body': getattr(e.request, 'body', '-'),
        }

        response_info = {
            'status_code': getattr(e.response, 'status_code', '-'),
            'reason': getattr(e.response, 'reason', '-'),
            'headers': dict(getattr(e.response, 'headers', {})),
            'content': getattr(e.response, 'text', '')[:500],
            'content_type': e.response.headers.get('content-type', '-') if e.response else '-',
            'content_length': e.response.headers.get('content-length', '-') if e.response else '-',
            'server': e.response.headers.get('server', '-') if e.response else '-',
            'date': e.response.headers.get('date', '-') if e.response else '-',
        }
        retry = seed.params.retry
        get_time = seed.params.get_time
        start_time = seed.params.start_time
        failed_time = seed.params.failed_time
        cost = failed_time - start_time

        log_data = {
            "stage": "http_error",
            "project": self.project,
            "task": self.task,
            "seed": seed.to_string, 
            "status_code": status_code,
            "request_info": request_info,
            "response_info": response_info,
            "retry": retry,
            "proxy": seed.params.proxy or '-',
            "exception_type": type(e).__name__,
            "exception_message": str(e),
            "traceback": seed.params.traceback or '-',
            "get_time": get_time,
            "start_time": start_time,
            "error_time": failed_time,
            "stage_cost": cost,
            "cost": cost,
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(failed_time)),
        }

        for key, value in log_data.items():
            if not isinstance(value, str):
                log_data[key] = json.dumps(value, ensure_ascii=False)
            else:
                log_data[key] = value

        contents = sorted(log_data.items())
        log_item.set_contents(contents)
        self._queue.push(log_item)

    def _build_exception_log(self, seed: Seed, e: Exception):
        log_item = LogItem()

        retry = seed.params.retry
        get_time = seed.params.get_time
        start_time = seed.params.start_time
        failed_time = seed.params.failed_time
        cost = failed_time - start_time

        log_data = {
            "stage": "exception",
            "project": self.project,
            "task": self.task,
            "seed": seed.to_string,
            "retry": retry,
            "exception_type": type(e).__name__,
            "exception_message": str(e),
            "traceback": seed.params.traceback or '-',
            "proxy": seed.params.proxy or '-',
            "get_time": get_time,
            "start_time": start_time,
            "error_time": failed_time,
            "stage_cost": cost,
            "cost": cost,
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(failed_time)),
        }

        for key, value in log_data.items():
            if not isinstance(value, str):
                log_data[key] = json.dumps(value, ensure_ascii=False)
            else:
                log_data[key] = value

        contents = sorted(log_data.items())
        log_item.set_contents(contents)
        self._queue.push(log_item)

    def _build_run(self):
        while not self._stop.is_set():
            try:
                items = []
                start_time = int(time.time())

                while len(items) < 1000:
                    log_item = self._queue.pop()
                    if not log_item or (int(time.time()) - start_time > 10):
                        break
                    items.append(log_item)

                if items:
                    request = PutLogsRequest(
                        project="databee-download-log",
                        logstore="log",
                        topic="cobweb",
                        logitems=items,
                        compress=True
                    )
                    self._client.put_logs(request=request)
            except Exception as e:
                logger.info(str(e))
