FROM python:3

COPY ./weather.py /run/
COPY ./requirements.txt /run/

RUN pip3 install -r /run/requirements.txt

CMD /run/weather.py
