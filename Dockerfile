FROM --platform=linux/amd64 python:3.12-alpine AS builder

WORKDIR /src

ENV POETRY_VERSION=1.8.2
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

COPY ["pyproject.toml", "poetry.lock", "/src"]
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

FROM --platform=linux/amd64 python:3.12-alpine

ENV PYTHONPATH=/src

WORKDIR /src

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY app /src/app
COPY .env /src

ENV HOST="0.0.0.0"
ENV PORT=8080

EXPOSE $PORT

CMD ["sh", "-c", "python app/manage.py runserver $HOST:$PORT"]
