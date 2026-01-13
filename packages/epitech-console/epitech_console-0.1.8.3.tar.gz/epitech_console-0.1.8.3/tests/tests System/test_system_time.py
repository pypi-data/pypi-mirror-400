import pytest
import time


from epitech_console.System import Time
from epitech_console import init, quit


init()



def test_time_wait(
    ) -> None:
        elapsed = Time.wait(0.05)

        assert 0.05 < elapsed < 0.06


quit(delete_log=True)
