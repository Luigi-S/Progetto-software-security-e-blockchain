FROM python:3.11-slim-buster

COPY . /app
COPY requirements.txt /app
COPY installSolcx.py /app

WORKDIR /app

RUN pip install -r requirements.txt
# Necessario per evitare errore di compilazione di solcx
RUN python installSolcx.py

ENTRYPOINT ["python"]

CMD ["main.py", "deploy" , "./contract.sol"]