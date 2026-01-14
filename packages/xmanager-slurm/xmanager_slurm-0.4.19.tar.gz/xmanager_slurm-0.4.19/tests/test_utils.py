import datetime as dt

import pytest

from xm_slurm import utils


@pytest.mark.parametrize(
    "timedelta_input,expected",
    [
        (dt.timedelta(seconds=30), "0-00:00:30"),
        (dt.timedelta(minutes=5), "0-00:05:00"),
        (dt.timedelta(hours=2), "0-02:00:00"),
        (dt.timedelta(days=3), "3-00:00:00"),
        (dt.timedelta(days=1, hours=2, minutes=30, seconds=45), "1-02:30:45"),
        (dt.timedelta(), "0-00:00:00"),
        (dt.timedelta(days=100, hours=23, minutes=59, seconds=59), "100-23:59:59"),
    ],
)
def test_timedelta_conversion(timedelta_input: dt.timedelta, expected: str) -> None:
    """Test conversion of timedelta to DD-HH:MM:SS format."""
    result = utils.timestr_from_timedelta(timedelta_input)
    assert result == expected
