import logging
from datetime import datetime

import pytz


class TaipeiTZFormatter(logging.Formatter):
    def converter(self, timestamp):
        try:
            dt = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        except TypeError:
            dt = datetime.now(tz=pytz.UTC)
        return dt.astimezone(pytz.timezone("Asia/Taipei"))

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat(timespec="seconds")
