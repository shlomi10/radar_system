FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config/ config/
COPY data/ data/
COPY radar/ radar/
COPY tests/ tests/
COPY main.py pytest.ini ./

ENTRYPOINT ["python", "main.py"]
CMD ["--config", "config/config.json", "--stream", "data/radar_stream.log"]
