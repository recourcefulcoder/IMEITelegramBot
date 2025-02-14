FROM python:3.12-alpine

RUN mkdir app

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

WORKDIR app_logic

CMD ["sanic", "server:app"]
