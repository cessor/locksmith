FROM alpine:latest
MAINTAINER Johannes Hofmeister <docker@spam.cessor.de>

RUN apk add --update bash curl g++ python3 python3-dev && \
    rm -rf /var/cache/apk/*

RUN curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
RUN python3 get-pip.py
RUN pip3 install tornado
RUN pip3 install requests

ADD ./locksmith /var/locksmith

CMD python3 /var/locksmith/serve.py
