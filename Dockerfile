
FROM python:3.9-alpine
LABEL maintainer="phyng"

RUN apk add --no-cache \
	curl \
	iputils \
	nginx

WORKDIR /usr/src/app
COPY . .
RUN rm data/*

# nginx
RUN mkdir -p /run/nginx
ADD ./config/nginx.conf /etc/nginx/http.d/default.conf

CMD nginx && python ./run.py --action schedule
