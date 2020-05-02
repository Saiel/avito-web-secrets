FROM python:3.7-alpine

WORKDIR /var/www
RUN apk add --no-cache gcc g++ musl-dev python3-dev libffi-dev openssl-dev

ADD ./requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir /run/sockets && chmod a+w /run/sockets

ADD ./start.sh .

CMD ["./start.sh"]
