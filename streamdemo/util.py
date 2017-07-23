# stdlib
from typing import Optional

# third party
from datetime import datetime


def datetime_to_secs(time: datetime, reftime: Optional[datetime]=datetime(1970, 1, 1)) -> float:
    return (time - reftime).total_seconds()
