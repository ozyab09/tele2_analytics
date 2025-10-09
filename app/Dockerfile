FROM python:3.14.0-slim-bookworm

COPY requirments.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirments.txt

CMD ["python3.14", "/app/collector.py"]

