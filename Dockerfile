FROM python:3.8-buster AS builder

COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.8-buster

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/stocks"

WORKDIR /usr/src/stocks

COPY --from=builder /root/.local /root/.local
COPY libs ./libs
COPY stocks.py .

ENTRYPOINT [ "python3", "stocks.py" ]
