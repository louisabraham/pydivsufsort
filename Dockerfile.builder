FROM python:3.12-alpine3.23 AS builder

RUN apk update --no-cache && apk add --no-cache build-base bash cmake git

# Upgrade pip
RUN pip install --upgrade pip
ENV CMAKE_POLICY_VERSION_MINIMUM=3.5
RUN pip cache purge
RUN pip install "pydivsufsort>=0.0.20" --index-url https://pypi.org/simple
RUN python -c "from pydivsufsort import common_substrings; print(common_substrings('hello','hello_world',3))"