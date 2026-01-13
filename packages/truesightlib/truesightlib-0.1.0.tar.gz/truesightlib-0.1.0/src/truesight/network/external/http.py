import requests


class Consumer:
    def __init__(self, api_key: str, method: str):
        self.logs_url = "http://localhost:8000/api/v1/external/logs/"
        self.api_key = api_key
        self.headers = {
            "Authorization": f"{self.api_key}",
        }
        self.method = method

    def sender(self, data, filename):
        try:
            files = {
                "file": (
                    f"{filename}.log",     
                    data,
                    "text/plain"
                )
            }
            request = requests.request(
                method=self.method,
                url=self.logs_url,
                files=files,
                headers=self.headers,
                timeout=3
            )
            print(request.text)
            return request.json()
        except Exception as error:
            return {"error": str(error)}
        