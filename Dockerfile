FROM python:3-buster AS base
ENV PATH=/srv/rp-discord/.local/bin/:/srv/rp-discord/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
RUN adduser --uid 1000 --disabled-password --gecos '' --home /srv/rp-discord rp-discord
WORKDIR /srv/rp-discord/rp-discord
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
COPY --chown=rp-discord poetry.lock pyproject.toml ./
USER rp-discord
RUN pip install --no-cache-dir --user poetry
RUN poetry install --no-dev


FROM base AS rp-discord
COPY --chown=rp-discord --from=pybuilder /srv/rp-discord/.local /srv/rp-discord/.local
COPY --chown=rp-discord . /srv/rp-discord/rp-discord/
COPY --chown=rp-discord ./entrypoint /srv/rp-discord/bin/entrypoint
USER rp-discord
ENTRYPOINT ["entrypoint"]
