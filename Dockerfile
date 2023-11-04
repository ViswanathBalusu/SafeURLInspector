FROM python:3.11-slim

LABEL authors="Chandra Kiran Viswanath Balusu"

WORKDIR /app

# install chbromium and dependencies
RUN apt update && apt install -y chromium chromium-l10n curl

COPY install.py .

#install latest chromium and chrome driver
RUN pip install -U pip && pip install requests && \
    python install.py && rm -rf install.py

# Install the Backend server
RUN pip install urlrakshak

#entrypoint
CMD ["URLRakshak"]