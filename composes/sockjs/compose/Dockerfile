FROM python:3.7-alpine

RUN apk update && apk --no-cache add bash gcc python3-dev musl-dev linux-headers

WORKDIR /tmp
COPY ./requirements .
RUN pip install --upgrade pip
RUN pip install -r ./prod.txt

WORKDIR /app/sockjs
