FROM alpine:latest
MAINTAINER Johannes Hofmeister

# Install Nginx.
RUN apk add --update bash curl nginx && \
    rm -rf /var/cache/apk/*

ADD nginx.conf /etc/nginx/nginx.conf

# Define working directory.
WORKDIR /etc/nginx

# Define default command.
CMD ["nginx"]

# Expose ports.
EXPOSE 8443
