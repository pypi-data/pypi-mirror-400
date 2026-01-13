import yaml
from datetime import datetime
from truesight.logger.handler import Sender


class Loader:
    def __init__(self, path="Vectorial.yaml"):
        self.path = path
        self.now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    def config(self, data):
        """this module is responsible to search and read
        yaml files following this pattern:

            Project:
                name:
                description:
                environment:
                
            Endpoints:
                - path: 
                method: 
                - path:
                method:

            Config:
                api_key:

            Logs:
                path:
            
        Args:
            path (str, optional): file path. Defaults to "Vectorial.yml".
        """
        with open(self.path) as f:
            config = yaml.safe_load(f)
            project = config.get("Project", [])
            endpoints = config.get("Endpoints", [])
            api_key = config.get("Config", []).get("api_key")

        try:
            sender = Sender(
                data=data,
                api_key=api_key,
                filename=f"{self.now}_vectorial_{api_key}.log"
            )
            sender.send()
            return {
                "message": "Success",
                "status": 201
            }
        except Exception as error:
            return {
                "message": error,
                "status": 400
            }