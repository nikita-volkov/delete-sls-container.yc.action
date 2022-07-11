FROM python:3.10.5-slim

RUN python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py /usr/local/bin/

ENTRYPOINT ["main.py"]
