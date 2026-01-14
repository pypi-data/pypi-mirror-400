from enum import IntEnum


class ActivityID(IntEnum):
    """
    0	Unknown The event activity is unknown.
    1	Log The discovered information is via a log.
    2	Collect The discovered information is via a collection process.
    99	Other The event activity is not mapped. See the activity_name attribute, which contains a data source specific value.
    """
    Unknown = 0
    Log = 1
    Collect = 2
    Other = 99
