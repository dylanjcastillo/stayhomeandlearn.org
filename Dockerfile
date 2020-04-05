FROM python:3

RUN  apt-get update -y && \
     apt-get upgrade -y && \
     apt-get clean
RUN apt-get install -y zip

COPY src build
RUN python3 -m pip install -r /build/requirements.txt -t build/
RUN mkdir -p target
CMD sh build/package.sh
