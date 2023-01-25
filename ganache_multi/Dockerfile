FROM trufflesuite/ganache:latest
WORKDIR /app
COPY setup.sh setup.sh
ENV PORTS=4
#ENV BASE_PORT=10000
ENTRYPOINT pip install "typer[all]" && ./setup.sh
