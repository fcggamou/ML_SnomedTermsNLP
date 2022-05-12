import utils
from datetime import datetime


def test_json_date_to_datetime():
    date = utils.json_date_to_datetime("2021-02-11T20:08:31.2818673-03:00")
    assert date.year == 2021
    assert date.month == 2
    assert date.day == 11
    assert date.hour == 20
    assert date.minute == 8
    assert date.second == 31


def test_datetime_to_sql():
    date = datetime(2020, 1, 2, 20, 30, 15)
    sql_date = utils.datetime_to_sql(date)
    assert sql_date == "2020-01-02 20:30:15"


def test_json_date_to_sql():
    sql_date = utils.json_date_to_sql("2021-02-11T20:08:31.2818673-03:00")
    assert sql_date == "2021-02-11 20:08:31"
