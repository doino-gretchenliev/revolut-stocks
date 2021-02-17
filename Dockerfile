FROM python:3.8-buster AS builder

COPY Pipfile .
COPY Pipfile.lock .
RUN python -m pip install pipenv
RUN python -m pipenv install

FROM python:3.8-buster

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/stocks"

WORKDIR /usr/src/stocks

COPY --from=builder /root/.local /root/.local
COPY libs ./libs
COPY stocks.py .

ENTRYPOINT [ "pipenv", "run", "start" ]
