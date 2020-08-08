FROM python:3.8.3
USER root

WORKDIR /bot

ADD . /bot

RUN pip install --trusted-host pypi.python.org -r requirements.txt

CMD ["python", "main.py"]
