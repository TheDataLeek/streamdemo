# stdlib
import time
# 3rd party
from datetime import datetime
# local
from ..util import datetime_to_secs


def test_datetime_to_secs():
    test_time = datetime.now()
    test_time_s = time.time()

    assert (datetime_to_secs(test_time) - test_time_s) <= 0.1
