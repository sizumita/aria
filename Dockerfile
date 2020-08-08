FROM python:3.8.3
USER root

WORKDIR /bot

ADD . /bot

CMD ["python", "main.py"]
