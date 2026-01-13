ARG FROM
FROM $FROM AS base
ARG POETRY_VERSION

WORKDIR /root

# install os components
RUN apt-get update && apt-get install -y --no-install-recommends \
  # tools
  curl \
  dnsutils \
  inetutils-ping \
  && rm -rf /var/lib/apt/lists/*


# poetry env
ENV POETRY_VERSION=$POETRY_VERSION \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR=/opt/poetry_cache


# app settings
ENV APP_PATH="/app"
ENV VENV_PATH="$APP_PATH/.venv"
ENV VIRTUAL_ENV=$VENV_PATH

# path
ENV PATH="$VIRTUAL_ENV/bin:$POETRY_HOME/bin:$PATH"


#RUN pip install toml

# install poetry uses env settings
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry config installer.max-workers 10
RUN poetry config experimental.new-installer false

RUN mkdir /app
WORKDIR /app

CMD ["python","--version"]

FROM base AS versionhack
WORKDIR /app

COPY poetry.lock pyproject.toml /app/
RUN poetry version 0.0.1

FROM base AS build
ENV EVENTIX_API_PORT=8000
WORKDIR /app

# install project production packages
COPY --from=versionhack /app/poetry.lock /app/pyproject.toml /app/
RUN poetry install --only main --no-interaction --no-ansi
#
## install code
COPY . /app/
EXPOSE $EVENTIX_API_PORT
#
CMD supervisord
## CMD python worker.py

HEALTHCHECK \
    --interval=60s \
    --timeout=10s \
    --start-period=2s \
    --start-interval=1s \
    --retries=3 \
    CMD curl --fail http://localhost:$EVENTIX_API_PORT/healthz || exit 1
