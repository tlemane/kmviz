FROM python

WORKDIR /home

RUN pip install kmviz==0.4.2 gunicorn
ENV KMVIZ_CONF=/home/config.toml

ENTRYPOINT ["gunicorn", "kmviz.app:app"]
CMD ["-w 4", "-b 0.0.0.0:8000"]

LABEL version="0.4.2"
LABEL description="kmviz"
LABEL author="Teo Lemane"
