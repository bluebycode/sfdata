FROM tiangolo/uwsgi-nginx-flask:flask-python3.5

RUN apt-get update \
    && apt-get install -y gcc \
    python-dev \
    libev4 libev-dev telnet

COPY requirements.txt /tmp/
RUN pip install -U pip \
    && pip install -r /tmp/requirements.txt

COPY ./app /app