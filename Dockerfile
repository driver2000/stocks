FROM python:3.7-slim

COPY ./requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "/app/run.py" ]