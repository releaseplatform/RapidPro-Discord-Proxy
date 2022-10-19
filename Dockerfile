FROM python:3-buster AS base
ENV PATH=/srv/rp-discord-proxy/.local/bin/:/srv/rp-discord-proxy/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
RUN adduser --uid 1000 --disabled-password --gecos '' --home /srv/rp-discord-proxy rp-discord-proxy
WORKDIR /srv/rp-discord-proxy/rp-discord-proxy
RUN apt-get -yq update \
        && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        unattended-upgrades \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean


FROM base AS pybuilder
ENV POETRY_VIRTUALENVS_CREATE=false
RUN apt-get -yq update \
        && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        build-essential \
        # psycopg2 deps
        libpq-dev \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean
COPY --chown=rp-discord-proxy poetry.lock pyproject.toml ./
RUN pip install --no-cache-dir poetry
RUN poetry install --only main
USER rp-discord-proxy


FROM base AS rp-discord-proxy
COPY --chown=rp-discord-proxy . /srv/rp-discord-proxy/rp-discord-proxy/
COPY --chown=rp-discord-proxy ./entrypoint /srv/rp-discord-proxy/bin/entrypoint
USER rp-discord-proxy
EXPOSE 8000
ENTRYPOINT ["entrypoint"]
