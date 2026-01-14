from typing import Optional, Literal
import datetime
import pytz
import obspy


def convert_starttime_from_naive_to_utc(
        starttime: obspy.core.UTCDateTime,
        timezone: Optional[Literal["Europe/Paris"]]) -> obspy.core.UTCDateTime:
    """
    :param starttime: a naive UTCDateTime : i.e. read as if it was an UTC+0 datetime
    :param timezone: the time zone, None means stay in naive mode
    """

    if timezone is None:
        # do not change starttime
        return starttime

    tz = pytz.timezone(timezone)

    # re-interpret the starttimes in the given timezone
    # DO NOT use the tzinfo field of datetime.datetime with pytz!!!
    local_time = datetime.datetime(
        year=starttime.year,
        month=starttime.month,
        day=starttime.day,
        hour=starttime.hour,
        minute=starttime.minute,
        second=starttime.second,
        microsecond=starttime.microsecond,
        #tzinfo=... NO!!!
        )#.astimezone(tz)  # fail on github CI
    local_time = tz.localize(local_time)

    # get the right timestamp in seconds since EPOCH, this value is independent of the timezone and refers to UTC+0
    true_timestamp_utc = local_time.timestamp()

    # recreate the UTCDateTime with the right timestamp
    starttime = obspy.core.UTCDateTime(true_timestamp_utc)

    return starttime


if __name__ == '__main__':

    # assule the file header indicates 2023/07/12 - 12h07 and we know it is a local time in Paris time zone

    t_naive = obspy.core.UTCDateTime(2023, 7, 12, 12, 7)
    print(t_naive, t_naive.timestamp)  # 2023-07-12T12:07:00.000000Z 1689163620.0

    t_utc = convert_starttime_from_naive_to_utc(t_naive, timezone="Europe/Paris")
    print(t_utc, t_utc.timestamp)  # 2023-07-12T10:07:00.000000Z 1689156420.0
