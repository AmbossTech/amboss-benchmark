FROM python:3.10-bullseye

WORKDIR /app

COPY . .
RUN pip config --user set global.progress_bar off
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/output

CMD ["python", "benchmark.py"]
