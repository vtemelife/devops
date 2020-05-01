FROM nginx:1.15.10-alpine
RUN apk update && apk --no-cache add bash

ARG NGINX_MODE=dev
COPY ./build /www
COPY ./compose/nginx_$NGINX_MODE.conf /etc/nginx/conf.d/default.conf
COPY ./ssl /etc/nginx/ssl

WORKDIR /app/client
