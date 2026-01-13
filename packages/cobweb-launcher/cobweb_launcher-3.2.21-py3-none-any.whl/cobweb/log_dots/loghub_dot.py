import json
import os
import time

from aliyun.log import LogClient, PutLogsRequest, LogItem
from .dot import Dot, logger, Event


class LoghubDot(Dot):

    def __init__(self, stop: Event, project: str, task: str):
        super().__init__(stop, project, task)
        self._client = LogClient(
            endpoint=os.getenv("DOT_LOGHUB_ENDPOINT"),
            accessKeyId=os.getenv("DOT_LOGHUB_ACCESS_KEY"),
            accessKey=os.getenv("DOT_LOGHUB_SECRET_KEY")
        )

    def _build_run(self):
        while not self._stop.is_set():
            try:
                items = []
                start_time = int(time.time())

                while len(items) < 1000 and (int(time.time()) - start_time) < 10:
                    log_data = self._queue.pop()

                    if not log_data:
                        break

                    for key, value in log_data.items():
                        if not isinstance(value, str):
                            log_data[key] = json.dumps(value, ensure_ascii=False)
                        else:
                            log_data[key] = value

                    log_item = LogItem()
                    contents = sorted(log_data.items())
                    log_item.set_contents(contents)
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

