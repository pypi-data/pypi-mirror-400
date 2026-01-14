import time

from teklia_toolbox.time import Timer


def test_timer():
    with Timer() as t:
        time.sleep(0.05)

    assert t.delta.total_seconds() >= 0.05
