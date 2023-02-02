FROM trufflesuite/ganache:latest
COPY . /ganache_data
WORKDIR /ganache_data

ENV PORTS=4
#ENV BASE_PORT=10000
ENTRYPOINT ./ganaches.sh