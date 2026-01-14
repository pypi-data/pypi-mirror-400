from datetime import datetime, timedelta


def iso_datetime(ts):
    return (ts).strftime("%Y-%m-%d %H:%M:%S")


def iso_date(ts):
    return f'{(ts).strftime("%Y-%m-%d")} 00:00:00'


def timestamp_from_unix_ts(ts):
    return iso_datetime(datetime.fromtimestamp(ts))


def today():
    return iso_date(datetime.today())


def yesterday():
    return iso_date(datetime.today() - timedelta(days=1))


def monday_of_this_week():
    return iso_date(datetime.today() - timedelta(days=datetime.today().weekday()))


def first_of_this_month():
    return iso_date(datetime.today().replace(day=1))


def next_day_from_iso(iso_ts):
    return iso_datetime(
        datetime.strptime(iso_ts, "%Y-%m-%d %H:%M:%S") + timedelta(days=1)
    )


def timestamp_normalize(ts):
    match ts:
        case "today":
            return today()
        case "yesterday":
            return yesterday()
        case "monday":
            return monday_of_this_week()
        case "first":
            return first_of_this_month()
        case _:
            return iso_date(datetime.strptime(ts, "%Y.%m.%d"))
