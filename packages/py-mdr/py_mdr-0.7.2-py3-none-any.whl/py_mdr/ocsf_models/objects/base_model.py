import datetime
from dataclasses import dataclass, asdict


@dataclass
class BaseModel:
    """
    Represents the base model for all OCSF related values.
    """

    @staticmethod
    def _cleanup_dict_values(d: dict):
        """
        Cleans up all the values that have:
            * None
            * Empty list
            * Empty dictionaries
        :param d:
        :return:
        """
        for key in list(d.keys()):
            # Delete if None
            if d[key] is None:
                del d[key]

            # Check elements within lists
            elif isinstance(d[key], list):
                for i in range(len(d[key])):
                    # Cleanup dictionaries within lists
                    if isinstance(d[key][i], dict):
                        BaseModel._cleanup_dict_values(d[key][i])
                        if len(d[key][i]) == 0:
                            d[key][i] = None

                # Remove all None values
                d[key] = [value for value in d[key] if value is not None]

                # Remove empty lists
                if len(d[key]) == 0:
                    del d[key]

            # Check recursively for dictionaries
            elif isinstance(d[key], dict):
                BaseModel._cleanup_dict_values(d[key])
                # Delete empty dicts
                if len(d[key]) == 0:
                    del d[key]

    @staticmethod
    def _convert_datetime(data: dict):
        """
        Tries to convert the given values to datetime
        :param data:
        :return:
        """
        for key in data.keys():
            if isinstance(data[key], dict):
                BaseModel._convert_datetime(data[key])
            elif isinstance(data[key], datetime.datetime):
                reported_date: datetime.datetime = data[key]
                # Conversion suggested here:
                # To milliseconds, documented here: https://docs.python.org/3/library/datetime.html#datetime.timedelta.total_seconds
                timezone = datetime.timezone.utc if reported_date.tzinfo is not None else None
                unix_epoch = datetime.datetime(1970,1,1, tzinfo=timezone)
                data[key] = (reported_date - unix_epoch) / datetime.timedelta(milliseconds=1)
                data[key] = None

    def as_dict(self, remove_empty=True):
        """
        Converts to a JSON serializable dictionary
        :param remove_empty:
        :return:
        """
        values = asdict(self)

        # Cleanup values
        if remove_empty:
            BaseModel._cleanup_dict_values(values)

        # Convert datetime
        BaseModel._convert_datetime(values)

        return values
