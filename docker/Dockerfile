FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmagic-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libmariadb-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/mayan-edms

COPY . .

RUN pip install --upgrade pip

# Key difference here: install project as a package
RUN pip install .

# Azure support (same as yours)
RUN pip install \
    "azure-storage-blob>=12.19.0" \
    "django-storages[azure]>=1.14.0" \
    "azure-identity>=1.15.0"

EXPOSE 8000

CMD ["gunicorn", "mayan.wsgi:application", "--bind", "0.0.0.0:8000"]
