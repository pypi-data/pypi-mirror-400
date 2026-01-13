from datetime import date, datetime, timedelta, timezone
from unittest import TestCase

from lotion.datetime_utils import convert_to_date_or_datetime

JST = timezone(timedelta(hours=+9), "JST")


class TestDatetime(TestCase):
    def test_日付だけ指定した場合でも日時で返す(self):
        # Given, When
        actual = convert_to_date_or_datetime("2021-01-01", cls=datetime)
        print(actual)

        # Then
        expected = datetime.fromisoformat("2021-01-01").replace(tzinfo=JST)
        print(expected)
        self.assertEqual(expected, actual)

    def test_0時0分の場合は日付として返却する(self):
        # Given, When
        actual = convert_to_date_or_datetime("2021-01-01 00:00:00+09:00")
        print(actual)

        # Then
        expected = date.fromisoformat("2021-01-01")
        print(expected)
        self.assertEqual(expected, actual)
