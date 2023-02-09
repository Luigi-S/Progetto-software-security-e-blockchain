FROM python:3.9-slim-buster
COPY . /py_backend
WORKDIR /py_backend
ENV PORTS=4
RUN pip install -r requirements.txt && python installSolcx.py
ENTRYPOINT python -u setup.py