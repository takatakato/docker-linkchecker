FROM python:2.7-alpine3.6

RUN apk add --update gcc g++ musl-dev \
	&& pip install linkchecker --upgrade \
	&& pip install requests==2.9.2

WORKDIR /app

ENTRYPOINT ["linkchecker"]

CMD ["-V"]
