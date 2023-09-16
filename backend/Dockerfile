FROM python:3.9-slim

WORKDIR /app

ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0 --access-logfile=/app/logs/access.log --error-logfile=/app/logs/error.log --log-level=debug"

EXPOSE 8000

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r ./requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]