FROM python:2.7-alpine3.6

RUN apk --no-cache add --virtual build-deps gcc g++ musl-dev \
	&& pip install linkchecker --upgrade \
	&& pip install requests==2.9.2 \
	&& pip install boto3 \
      	&& apk del --purge -r build-deps

RUN mkdir -p /.linkchecker/plugins

WORKDIR /linkchecker
ADD ./linkchecker.py /linkchecker

USER nobody

ENTRYPOINT ["python", "linkchecker.py"]
