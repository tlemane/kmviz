FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /home

RUN apt-get update
RUN apt-get install -y --no-install-recommends python3 python3-pip
RUN apt-get clean

RUN pip install kmviz==0.2.0 gunicorn

ENV KMVIZ_CONF=/home/config.toml

ENTRYPOINT ["gunicorn", "kmviz.app:app"]
CMD ["-w 4", "-b 0.0.0.0:8000"]

LABEL version="0.2.0"
LABEL description="kmviz"
LABEL author="Teo Lemane"
