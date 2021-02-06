FROM python:3.9-slim AS requirements

WORKDIR /cronjobs

COPY . .

RUN find . -type f -not -name 'requirements.txt' -exec rm -rfv '{}' \;

FROM python:3.9-slim AS build

WORKDIR /cronjobs

RUN apt update \
    && apt install -y \
    build-essential \
    libffi-dev \
    libxml2-dev \
    libxslt-dev

COPY --from=requirements /cronjobs .

# install dependencies for mirror-tv's schedule
RUN set -x \
    && cd /cronjobs/mirror-tv/schedule \
    && for dir in */ ; \
    do if cd /cronjobs/mirror-tv/schedule/$dir \
    && python3 -m venv .venv \
    && . .venv/bin/activate \
    && pip3 install --upgrade pip \
    && pip3 install --upgrade setuptools \
    && pip3 install -r ./requirements.txt \
    && deactivate; then echo "done"; else exit 1; fi ; \
    done

# install dependencies for mirror-tv's feed
RUN set -x \
    && cd /cronjobs/mirror-tv/feed \
    && for dir in */ ; \
    do if cd /cronjobs/mirror-tv/feed/$dir \
    && python3 -m venv .venv \
    && . .venv/bin/activate \
    && pip3 install --upgrade pip \
    && pip3 install --upgrade setuptools \
    && pip3 install -r ./requirements.txt \
    && deactivate; then echo "done"; else exit 1; fi ; \
    done

FROM python:3.9-slim

WORKDIR /cronjobs

COPY --from=build /cronjobs .
COPY . .