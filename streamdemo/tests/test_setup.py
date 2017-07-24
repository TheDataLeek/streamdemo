# stdlib
# 3rd party
from datetime import datetime
from datetime import timedelta
# local
from ..setup import random_week_time


def test_random_week_time():
    stime = datetime.now()
    for _ in range(1000):
        assert (random_week_time() - stime) <= timedelta(weeks=1)


