FROM python:3.8-slim

# Maintainers
LABEL maintainer="API Management Team"

# Create working directory
RUN mkdir -p /tests/

COPY "." "/tests"
RUN pip install --upgrade pip
RUN pip install -r /var/api_tests/requirements.txt

WORKDIR "/var/api_tests/"

ENV PYTHONPATH=/var/api-tests/:

CMD tail -f /dev/null
