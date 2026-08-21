FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config/ config/
COPY data/ data/
COPY radar/ radar/
COPY tests/ tests/
COPY ui/ ui/
COPY main.py pytest.ini ./

ENV RADAR_UI_HOST=0.0.0.0
ENV PORT=8765
EXPOSE 8765

ENTRYPOINT ["python"]
CMD ["-m", "ui.app"]
