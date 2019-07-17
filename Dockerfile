FROM python:3.7

WORKDIR /app

ADD . /app

RUN apt-get update && apt-get install -y libsm6 libxrender1 libfontconfig1 \
    && pip install -r requirments.txt \
    && apt-get clean

EXPOSE 5000

CMD python server.py