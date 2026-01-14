from obspy.core import UTCDateTime
from readdat.utils.timeconversion import convert_starttime_from_naive_to_utc


def test_datetime_conversion():
    starttime = UTCDateTime(2023, 9, 27, 12, 43, 12, 1)
    ans = convert_starttime_from_naive_to_utc(
        starttime=starttime,
        timezone ="Europe/Paris")
    assert str(starttime) == "2023-09-27T12:43:12.000001Z", (str(starttime), "2023-09-27T12:43:12.000001Z")
    assert str(ans) == "2023-09-27T10:43:12.000001Z", (str(ans), "2023-09-27T10:43:12.000001Z")
