FROM python:3.9-slim-buster
COPY . /py_backend
WORKDIR /py_backend
RUN pip install -r requirements.txt && python install_solcx.py
ENTRYPOINT python -u setup.py