FROM python:3

RUN pip3 install requests

COPY ./weather_test.py /run

CMD /run/weather_test.py
