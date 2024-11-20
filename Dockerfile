FROM python:3.9 AS base

WORKDIR /app/src

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./src /app/src

RUN mkdir /app/logs

FROM base as test

COPY ./tests /app/tests

ENV PYTHONPATH=/app

FROM base as final

EXPOSE 8000

ENTRYPOINT ["gunicorn", "main:app", "--bind", "0.0.0.0:8000", "-k", "uvicorn_worker.UvicornWorker"]