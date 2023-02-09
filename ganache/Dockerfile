FROM trufflesuite/ganache:latest
COPY . /ganache
WORKDIR /ganache
ENV PORTS=4
RUN chmod 755 ganaches.sh
ENTRYPOINT ./ganaches.sh