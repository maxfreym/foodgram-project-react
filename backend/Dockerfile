FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r ./requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:10000", "--error-logfile", "/etc/gunicorn/log/error.log", "--access-logfile", "/etc/gunicorn/log/access.log"]