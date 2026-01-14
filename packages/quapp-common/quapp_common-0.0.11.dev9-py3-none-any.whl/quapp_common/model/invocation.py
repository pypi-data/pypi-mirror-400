#  Quapp Platform Project
#  invocation.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.
import logging
import traceback as tb
from dataclasses import dataclass
from datetime import datetime


class Event:
    logger = logging.getLogger("model.Invocation.Event")
    logger.setLevel(logging.DEBUG)

    def __init__(self, request):
        self.request_body = {}
        self.request = request

    def json(self):
        return self.request_body


@dataclass
class Result:
    def __init__(self):
        self.timestamp: datetime = datetime.now()

    def serialize(self):
        return {
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class Success(Result):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def serialize(self):
        serialize = super().serialize()
        serialize['data'] = self.data
        return serialize


@dataclass
class Error(Result):
    def __init__(self, error: Exception):
        super().__init__()
        self.error = tb.format_exception(error)

    def serialize(self):
        serialize = super().serialize()
        serialize['error'] = self.error
        return serialize
