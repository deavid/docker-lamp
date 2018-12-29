FROM debian:stretch

RUN echo "deb http://ftp.debian.org/debian stretch-backports main" \
  > /etc/apt/sources.list.d/backports.list

RUN set -ex \
	&& apt-get update \
	&& apt-get install -y -t stretch-backports \
		certbot \
	&& rm -rf /var/lib/apt/lists/*

COPY renew.sh /

CMD ["bash", "/renew.sh"]
