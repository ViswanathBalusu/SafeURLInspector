FROM python:3.11-slim

LABEL authors="Chandra Kiran Viswanath Balusu"

WORKDIR /app

RUN apt update && apt install -y chromium chromium-l10n curl

COPY install.py .

RUN python install.py && rm -rf install.py && \
    pip install -U pip && pip install urlrakshak

CMD ["URLRakshak"]