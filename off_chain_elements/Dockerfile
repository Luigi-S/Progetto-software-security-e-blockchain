FROM python:3.9-slim-buster

COPY . /off_chain_elements
COPY checker.py /off_chain_elements
#COPY installSolcx.py /app
#COPY bytecode.json /app
#COPY abi.json /app

WORKDIR /off_chain_elements

#RUN pip install -r requirements.txt
# Necessario per evitare errore di compilazione di solcx
#RUN python installSolcx.py

ENTRYPOINT ["python"]

CMD ["checker.py"]