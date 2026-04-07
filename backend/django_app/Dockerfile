FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps:
#   default-libmysqlclient-dev + pkg-config  → needed to build mysqlclient
#   gcc                                      → C compiler for native extensions
#   libjpeg-dev zlib1g-dev libfreetype6-dev  → Pillow image support
#   netcat-openbsd                           → wait logic in entrypoint
#   curl                                     → healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc default-libmysqlclient-dev pkg-config \
    libjpeg-dev zlib1g-dev libfreetype6-dev \
    netcat-openbsd curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
