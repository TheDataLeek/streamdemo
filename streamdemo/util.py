# stdlib
from typing import Optional

# third party
from datetime import datetime


def datetime_to_secs(time: datetime, reftime: Optional[datetime]=datetime(1970, 1, 1)) -> float:
    """
    Convert datetime to seconds since epoch (or some other reftime)
    """
    return (time - reftime).total_seconds()
