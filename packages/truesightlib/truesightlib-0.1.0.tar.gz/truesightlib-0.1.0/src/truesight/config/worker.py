import json
import time
from truesight.network.external.http import Consumer


class LogFileSender:
    def __init__(self, filepath, api_key):
        self.filepath = filepath
        self.api_key = api_key

    def run(self):
        while True:
            self._process_file()
            time.sleep(5)

    def _process_file(self):
        try:
            with open(self.filepath, "r") as f:
                lines = f.readlines()

            if not lines:
                return
            
            for line in lines:
                data = json.loads(line)
                consumer = Consumer(
                    data=data,
                    api_key=self.api_key,
                    method="POST"
                )
                consumer.sender()

            open(self.filepath, "w").close()

        except Exception as error:
            pass