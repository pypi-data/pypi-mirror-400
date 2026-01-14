import sqlite3
from pathlib import Path

DATABASE_PATH = Path.home() / ".pyflo.db"


def database():
    connection = sqlite3.connect(DATABASE_PATH)
    return connection


def init():
    connection = database()
    cursor = connection.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT NOT NULL,
        start_ts TEXT NOT NULL,
        end_ts TEXT NOT NULL
    )"""
    )
    connection.commit()
    connection.close()


def database_log(label, start_ts, end_ts):
    connection = database()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO log (label, start_ts, end_ts)
        VALUES (?, ?, ?)
    """,
        (label, start_ts, end_ts),
    )
    connection.commit()
    connection.close()


def database_duration_query(start_ts, end_ts, by, filters):
    connection = database()
    cursor = connection.cursor()
    between = "WHERE start_ts >= ? AND end_ts <= ?"
    filter = (
        f"AND label IN ({', '.join('?' for _ in filters)})" if len(filters) > 0 else ""
    )
    duration_seconds = """
        SUM(
            strftime('%s', end_ts) - strftime('%s', start_ts)
        ) AS duration_seconds
    """
    if by == "week":
        query_string = f"""
        SELECT strftime('%w', start_ts) AS weekday, {duration_seconds}
        FROM log
        {between} {filter}
        GROUP BY weekday
        ORDER BY weekday
        """
    if by == "day":
        query_string = f"""
        SELECT strftime('%H', start_ts) AS hour, {duration_seconds}
        FROM log
        {between} {filter}
        GROUP BY hour
        ORDER BY hour
        """
    if by == "label":
        query_string = f"""
        SELECT label, {duration_seconds}
        FROM log
        {between} {filter}
        GROUP BY label
        ORDER BY duration_seconds DESC
        """
    args = (start_ts, end_ts, *filters)
    result = cursor.execute(query_string, args)
    return normalize_duration_query_result(result.fetchall(), by)


def normalize_duration_query_result(data, by):
    weekdays = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    if by == "week":
        l = [(x, 0) for x in weekdays]
    if by == "day":
        l = [(f"{x:02}:00", 0) for x in range(24)]
    if by == "label":
        return data
    for i, x in enumerate(data):
        index = int(x[0])
        l[index] = (l[index][0], x[1])
    return l


def database_list_labels(filters):
    connection = database()
    cursor = connection.cursor()
    where = " OR ".join(["label LIKE ?"] * len(filters))
    where = "WHERE " + where if len(filters) > 0 else ""
    result = cursor.execute(
        f"SELECT label FROM log {where}", tuple(f"%{x}%" for x in filters)
    )
    return "\n".join([x[0] for x in result.fetchall()])


init()
