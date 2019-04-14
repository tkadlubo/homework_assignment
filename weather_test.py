#!/usr/bin/env python3

import datetime
import os
import unittest

import requests

class TestWeather(unittest.TestCase):
    def setUp(self):
        self.weather_server = os.getenv("WEATHER_HOST")

    def test_get_temperatures_returns_json(self):
        response = requests.get("http://{}/temperatures?start=2018-08-01T00:00:00Z&end=2018-08-07T00:00:00Z".format(self.weather_server))
        self.assertEqual(200, response.status_code)
        self.assertEqual(7, len(response.json()))

    def test_get_speeds_returns_json(self):
        response = requests.get("http://{}/speeds?start=2018-08-01T00:00:00Z&end=2018-08-07T00:00:00Z".format(self.weather_server))
        self.assertEqual(200, response.status_code)
        self.assertEqual(7, len(response.json()))

    def test_get_weather_returns_json(self):
        response = requests.get("http://{}/weather?start=2018-08-01T00:00:00Z&end=2018-08-07T00:00:00Z".format(self.weather_server))
        self.assertEqual(200, response.status_code)
        self.assertEqual(7, len(response.json()))

    def test_incorrect_dates_returns_400(self):
        response = requests.get("http://{}/temperatures?foo&end=bar".format(self.weather_server))
        self.assertEqual(400, response.status_code)

    def test_inconsistent_dates_returns_400(self):
        response = requests.get("http://{}/temperatures?end=2018-08-01T00:00:00Z&start=2018-08-07T00:00:00Z".format(self.weather_server))
        self.assertEqual(400, response.status_code)

    def test_no_start_returns_400(self):
        response = requests.get("http://{}/temperatures?end=2018-08-01T00:00:00Z".format(self.weather_server))
        self.assertEqual(400, response.status_code)

    def test_no_end_returns_400(self):
        response = requests.get("http://{}/temperatures?start=2018-08-01T00:00:00Z".format(self.weather_server))
        self.assertEqual(400, response.status_code)

    def test_no_data_before_1900(self):
        response = requests.get("http://{}/temperatures?start=1899-08-01T00:00:00Z&end=1899-08-07T00:00:00Z".format(self.weather_server))
        self.assertEqual(400, response.status_code)

    def test_no_data_in_the_future(self):
        tomorrow = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(1)
        print(tomorrow)
        response = requests.get("http://{}/temperatures?start=2018-08-01T00:00:00+00:00&end={}".format(self.weather_server, tomorrow.isoformat('T', 'seconds')))
        self.assertEqual(400, response.status_code)

if __name__ == '__main__':
    unittest.main()
