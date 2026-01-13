import logging
import io
import queue
from truesight.network.external.http import Consumer


class Sender(logging.Logger):
    def __init__(self, data, api_key, filename):
        self._log_queue = queue.Queue(maxsize=10000)
        self.consumer = Consumer(
            api_key=api_key,
            method="POST"
        )
        self.data = data
        self.buffer = io.BytesIO()
        self.filename = filename

    def send(self):
        try:
            self.buffer.write(self.data.encode("utf-8"))
            self.buffer.seek(0)
            self.consumer.sender(self.buffer, self.filename)
        except Exception as error:
            return {"message": error}
        
        