FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install OS-level dependencies
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

# Set working directory
WORKDIR /opt/mayan-edms

# Copy all local source code into container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements/base.txt

# Install Azure-related packages (custom)
RUN pip install \
    "azure-storage-blob>=12.19.0" \
    "django-storages[azure]>=1.14.0" \
    "azure-identity>=1.15.0"

# Collect static files (optional depending on entrypoint)
RUN python manage.py collectstatic --noinput || echo "Skipping static collection"

# Port
EXPOSE 8000

# Default command (can override in compose)
CMD ["gunicorn", "mayan.wsgi:application", "--bind", "0.0.0.0:8000"]
