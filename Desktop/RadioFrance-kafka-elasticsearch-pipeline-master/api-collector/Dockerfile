FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY radiofrance_realtime_collector.py .

CMD ["python", "-u", "radiofrance_realtime_collector.py"]
