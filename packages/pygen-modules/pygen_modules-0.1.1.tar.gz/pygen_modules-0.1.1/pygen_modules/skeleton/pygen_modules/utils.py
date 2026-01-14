import datetime
import logging
from typing import Any


# Response utilities
class ResponseUtils:
    class getLogLevel:
        INFO = "INFO"
        ERROR = "ERROR"

    @staticmethod
    def responseWithData(success: bool, code: int, message: str, data: Any, **optional):
        response = {"status": success, "status_code": code, "message": message, "data": data}
        
        if optional:
            response.update(optional)
        return response

    @staticmethod
    def responseWithoutData(success: bool, code: int, message: str, **optional):
        return {"status": success, "status_code": code, "message": message}

    @staticmethod
    def logger(module_name: str, level: str, message: str):
        log_level = (
            logging.INFO if level == ResponseUtils.getLogLevel.INFO else logging.ERROR
        )
        logging.basicConfig(
            format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s", level=log_level
        )
        logger = logging.getLogger(module_name)
        logger.log(log_level, message)

    @staticmethod
    def get_current_datetime():
        return datetime.datetime.now()
