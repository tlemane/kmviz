FROM python

WORKDIR /home

RUN pip install kmviz==0.6.3 gunicorn
ENV KMVIZ_CONF=/home/config.toml

ENTRYPOINT ["python", "-m", "kmviz", "app", "deploy"]
CMD ["-u 0.0.0.0", "-p 8000", "-w 4"]

LABEL version="0.6.3"
LABEL description="kmviz"
LABEL author="Teo Lemane"
