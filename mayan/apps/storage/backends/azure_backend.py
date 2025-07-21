import logging
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from storages.backends.azure_storage import AzureStorage

from mayan.apps.storage.classes import DefinedStorage

logger = logging.getLogger(__name__)

@deconstructible
class MayanAzureStorage(AzureStorage):
    """
    Custom Azure Storage backend optimized for Mayan EDMS
    """
    def __init__(self, **kwargs):
        # Set default parameters for Mayan EDMS
        kwargs.setdefault('overwrite_files', False)
        kwargs.setdefault('object_parameters', {
            'cache_control': 'public, max-age=86400',
            'content_disposition': 'inline'
        })
        super().__init__(**kwargs)
    
    def get_object_parameters(self, name):
        """
        Override to set content type and disposition for documents
        """
        params = super().get_object_parameters(name)
        
        # Ensure documents are displayed inline for preview
        if name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.tiff')):
            params['content_disposition'] = 'inline'
        
        return params
    
    def _save(self, name, content):
        """
        Override to add logging and error handling
        """
        try:
            logger.debug(f"Saving file to Azure: {name}")
            return super()._save(name, content)
        except Exception as e:
            logger.error(f"Error saving file {name} to Azure: {e}")
            raise
    
    def delete(self, name):
        """
        Override to add logging and graceful error handling
        """
        try:
            logger.debug(f"Deleting file from Azure: {name}")
            super().delete(name)
        except ResourceNotFoundError:
            logger.warning(f"File not found for deletion: {name}")
        except Exception as e:
            logger.error(f"Error deleting file {name} from Azure: {e}")
            raise


class MayanDocumentAzureStorage(MayanAzureStorage):
    """Storage backend specifically for document files"""
    def __init__(self, **kwargs):
        kwargs.setdefault('azure_container', settings.AZURE_DOCUMENTS_CONTAINER)
        super().__init__(**kwargs)


class MayanCacheAzureStorage(MayanAzureStorage):
    """Storage backend for cached files (thumbnails, previews)"""
    def __init__(self, **kwargs):
        kwargs.setdefault('azure_container', settings.AZURE_CACHE_CONTAINER)
        kwargs.setdefault('overwrite_files', True)  # Cache files can be overwritten
        super().__init__(**kwargs)


class MayanSharedUploadedFileAzureStorage(MayanAzureStorage):
    """Storage backend for shared uploaded files"""
    def __init__(self, **kwargs):
        kwargs.setdefault('azure_container', settings.AZURE_SHARED_CONTAINER)
        super().__init__(**kwargs)