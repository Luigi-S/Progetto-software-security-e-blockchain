FROM trufflesuite/ganache:v7.7.3
WORKDIR /app
COPY setup.sh setup.sh
ENV PORTS=4
#ENV BASE_PORT=10000
ENTRYPOINT ./setup.sh
