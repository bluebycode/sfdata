FROM cassandra:3.11.3
LABEL author="vrandkode@gmail.com"
RUN apt-get update && apt-get install -y \
    wget \
    python \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /opt/datasets
COPY tools/ /opt/
COPY ./docker-entrypoint-initdb.d/ /docker-entrypoint-initdb.d/
RUN cd /opt/ && python mega.py 'https://mega.nz/#!GqRlAaRC!r5zOJxSZwXe40ov_7zhqiLqThOij804K9g73y_Q_DaA' \
    && mv mega_GqRlAaRC_incidents.all.csv /opt/datasets/incidents.all.csv

