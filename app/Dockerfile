FROM python:3.8.5-slim-buster

COPY requirments.txt /tmp/

RUN pip3 install -r /tmp/requirments.txt

CMD ["python3.8", "/app/collector.py"]