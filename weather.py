#!/usr/bin/env python3

import datetime
import json
import os

import dateutil.parser
import treq
from klein import Klein
from twisted.internet import defer

WIND_HOST=os.getenv("WIND_HOST")
TEMP_HOST=os.getenv("TEMP_HOST")

def date_range(start, end):
    now = start
    while now <= end:
        yield now
        now += datetime.timedelta(days=1)

async def async_get_many(urls):
    responses = await defer.DeferredList([treq.get(u) for u in urls])
    contents = await defer.DeferredList([treq.content(response[1]) for response in responses])
    return responses, contents

class WeatherServer(object):
    app = Klein()

    @app.route('/temperatures')
    async def temperatures(self, request):
        await self.aggregate_data_source(request, TEMP_HOST)

    @app.route('/speeds')
    async def speeds(self, request):
        await self.aggregate_data_source(request, WIND_HOST)

    async def aggregate_data_source(self, request, endpoint):
        start, end = self.parse_dates(request)
        if not start and not end:
            return

        responses, contents = await async_get_many(self.urls_for_date_range(endpoint, start, end))
        if not self.validate_responses(responses, contents):
            return

        defer.returnValue(json.dumps([json.loads(c[1]) for c in contents]))

    @app.route('/weather')
    async def weather(self, request):
        start, end = self.parse_dates(request)
        if not start and not end:
            return

        wind_responses, wind_contents = await async_get_many(self.urls_for_date_range(WIND_HOST, start, end))
        if not self.validate_responses(wind_responses, wind_contents):
            return

        temp_responses, temp_contents = await async_get_many(self.urls_for_date_range(TEMP_HOST, start, end))
        if not self.validate_responses(temp_responses, temp_contents):
            return

        response_data = []
        for i in range(len(wind_responses)):
            temp_data = json.loads(temp_contents[1][1])
            wind_data = json.loads(wind_contents[1][1])
            wind_data["temp"] = temp_data["temp"]
            response_data.append(wind_data)

        defer.returnValue(json.dumps(response_data))

    def parse_dates(self, request):
        try:
            start = request.args.get(b'start')[0]
            start = dateutil.parser.parse(start)

            end = request.args.get(b'end')[0]
            end = dateutil.parser.parse(end)
        except:
            request.setResponseCode(400)
            defer.returnValue("{'error': 'invalid date parameters'}")
            return

        print(end)
        print(start)
        print(datetime.datetime.now(end.tzinfo))
        if end < start or start.year < 1900:
            request.setResponseCode(400)
            defer.returnValue("{'error': 'invalid date parameters'}")
            return

        if end > datetime.datetime.now(end.tzinfo):
            request.setResponseCode(400)
            defer.returnValue("{'error': 'invalid date parameters'}")

        return start, end

    def urls_for_date_range(self, endpoint, start, end):
        return [ "http://{}?at={}".format(endpoint, day.isoformat()) for day in date_range(start, end) ]

    def validate_responses(self, responses, contents):
        for r in responses:
            if r[0] is False or r[1].code != 200:
                request.setResponseCode(500)
                defer.returnValue("{'error': 'couldn\'t access data'}")
                return False

        for c in contents:
            if c[0] is False:
                request.setResponseCode(500)
                defer.returnValue("{'error': 'couldn\'t access data'}")
                return False

        return True

if __name__ == "__main__":
    server = WeatherServer()
    server.app.run("0.0.0.0", int(os.getenv("PORT")))

