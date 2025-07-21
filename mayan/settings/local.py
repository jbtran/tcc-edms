import os
from azure.identity import DefaultAzureCredential

# Azure Storage Configuration
AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME', 'your-storage-account')
AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY', 'your-account-key')
AZURE_CONNECTION_STRING = os.environ.get('AZURE_CONNECTION_STRING', '')

# Azure Containers
AZURE_DOCUMENTS_CONTAINER = os.environ.get('AZURE_DOCUMENTS_CONTAINER', 'documents')
AZURE_CACHE_CONTAINER = os.environ.get('AZURE_CACHE_CONTAINER', 'cache')
AZURE_SHARED_CONTAINER = os.environ.get('AZURE_SHARED_CONTAINER', 'shared')

# Use Managed Identity in production (optional)
USE_AZURE_MANAGED_IDENTITY = os.environ.get('USE_AZURE_MANAGED_IDENTITY', 'False').lower() == 'true'

# Azure Storage Options
AZURE_STORAGE_OPTIONS = {
    'account_name': AZURE_ACCOUNT_NAME,
    'overwrite_files': False,
    'location': '',
    'file_overwrite': False,
    'custom_domain': f'{AZURE_ACCOUNT_NAME}.blob.core.windows.net',
    'url_expiration_secs': 3600,  # 1 hour for private URLs
}

if USE_AZURE_MANAGED_IDENTITY:
    AZURE_STORAGE_OPTIONS['token_credential'] = DefaultAzureCredential()
else:
    if AZURE_CONNECTION_STRING:
        AZURE_STORAGE_OPTIONS['connection_string'] = AZURE_CONNECTION_STRING
    else:
        AZURE_STORAGE_OPTIONS['account_key'] = AZURE_ACCOUNT_KEY

# Django Storage Configuration (Django 4.2+ format)
STORAGES = {
    'default': {
        'BACKEND': 'mayan.apps.storage.backends.azure_backend.MayanDocumentAzureStorage',
        'OPTIONS': {
            **AZURE_STORAGE_OPTIONS,
            'azure_container': AZURE_DOCUMENTS_CONTAINER,
        }
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    }
}

# Mayan EDMS Storage Backends
STORAGE_BACKEND_ARGUMENTS = {
    'mayan.apps.documents.storage_backends.DocumentFileStorage': {
        'backend_class': 'mayan.apps.storage.backends.azure_backend.MayanDocumentAzureStorage',
        'backend_arguments': {
            **AZURE_STORAGE_OPTIONS,
            'azure_container': AZURE_DOCUMENTS_CONTAINER,
        }
    },
    'mayan.apps.file_caching.storage_backends.CachePartitionFile': {
        'backend_class': 'mayan.apps.storage.backends.azure_backend.MayanCacheAzureStorage',
        'backend_arguments': {
            **AZURE_STORAGE_OPTIONS,
            'azure_container': AZURE_CACHE_CONTAINER,
        }
    },
    'mayan.apps.converter.storage_backends.ConverterCachePartitionFile': {
        'backend_class': 'mayan.apps.storage.backends.azure_backend.MayanCacheAzureStorage',
        'backend_arguments': {
            **AZURE_STORAGE_OPTIONS,
            'azure_container': AZURE_CACHE_CONTAINER,
        }
    },
    'mayan.apps.storage.backends.SharedUploadedFileStorage': {
        'backend_class': 'mayan.apps.storage.backends.azure_backend.MayanSharedUploadedFileAzureStorage',
        'backend_arguments': {
            **AZURE_STORAGE_OPTIONS,
            'azure_container': AZURE_SHARED_CONTAINER,
        }
    }
}

# Disable local storage optimization since we're using cloud storage
MAYAN_COMMON_DISABLE_LOCAL_STORAGE = True

# Media URL configuration for Azure
MEDIA_URL = f'https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_DOCUMENTS_CONTAINER}/'

# Cache configuration for better performance with cloud storage
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'mayan',
        'TIMEOUT': 86400,  # 24 hours
    }
}

# File upload settings optimized for cloud storage
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'mayan.apps.storage.backends.azure_backend': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}