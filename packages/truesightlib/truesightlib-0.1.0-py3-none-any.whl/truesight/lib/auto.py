from truesight.logger.handler import Sender
from truesight.config.loader import Loader


def auto_init():
    interpreter = Loader()
    config = interpreter.load_config()
    config.get("Logs")
    handler = Sender(config)
