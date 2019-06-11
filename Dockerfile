FROM python:3.6-alpine3.9

ADD requirements.txt /requirements.txt

RUN apk add --no-cache ca-certificates build-base && \
  pip install --upgrade pip && \
  pip install -r /requirements.txt && \
  apk del build-base

ADD *.py /

ENTRYPOINT ["python"]
