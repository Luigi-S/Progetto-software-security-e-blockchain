FROM python:3.9-slim-buster
COPY . /app
WORKDIR /app
RUN echo "\nstty erase ^?\nstty erase ^H" >> $HOME/.bashrc && pip install -r requirements.txt && python install_solcx.py
ENTRYPOINT tail -F anything