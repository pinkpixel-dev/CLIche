# syntax=docker/dockerfile:1
FROM python:3.12-alpine

WORKDIR /durdraw
COPY . .
RUN pip install --upgrade .
#RUN ./installconf.sh
ENV TERM=xterm-256color
ENTRYPOINT ["durdraw"]
