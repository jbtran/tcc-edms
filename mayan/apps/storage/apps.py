from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.acls.permissions import permission_acl_edit, permission_acl_view
from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.menus import menu_object, menu_tools
from mayan.apps.events.classes import EventModelRegistry, ModelEventType
from mayan.apps.navigation.classes import SourceColumn

from .classes import DefinedStorage
from .events import event_download_file_downloaded
from .links import (
    link_download_file_delete, link_download_file_download,
    link_download_file_list
)
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from mayan.apps.common.classes import ModelCopy
from mayan.apps.common.menus import menu_tools

from .classes import DefinedStorage


class StorageApp(AppConfig):
    has_tests = True
    name = 'mayan.apps.storage'
    verbose_name = _('Storage')

    def ready(self):
        super().ready()

        # Register Azure storage backends
        from .backends.azure_backend import (
            MayanDocumentAzureStorage,
            MayanCacheAzureStorage,
            MayanSharedUploadedFileAzureStorage
        )

        # Document file storage
        DefinedStorage(
            app_label='documents',
            backend_class=MayanDocumentAzureStorage,
            defined_storage_name='documents__documentfile',
            label=_('Document file storage'),
        )

        # Cache storage
        DefinedStorage(
            app_label='file_caching',
            backend_class=MayanCacheAzureStorage,
            defined_storage_name='file_caching__cache',
            label=_('File cache storage'),
        )

        # Shared upload storage
        DefinedStorage(
            app_label='storage',
            backend_class=MayanSharedUploadedFileAzureStorage,
            defined_storage_name='storage__shareduploadedfile',
            label=_('Shared uploaded file storage'),
        )

        # Import existing storage configurations
        from .links import link_download_file
        from .tasks import task_shared_uploaded_file_delete

        menu_tools.bind_links(
            links=(link_download_file,),
            sources=(
                'storage:download_file_list',
            )
        )

        ModelCopy(
            bind_link=True, register_permission=True
        ).add_to_model(model=self.get_model('DownloadFile'))

class StorageApp(MayanAppConfig):
    app_namespace = 'storage'
    app_url = 'storage'
    has_tests = True
    name = 'mayan.apps.storage'
    verbose_name = _('Storage')

    def ready(self):
        super().ready()
        DefinedStorage.load_modules()

        DownloadFile = self.get_model(model_name='DownloadFile')

        EventModelRegistry.register(model=DownloadFile)

        ModelEventType.register(
            model=DownloadFile, event_types=(
                event_download_file_downloaded,
            )
        )

        ModelPermission.register(
            model=DownloadFile, permissions=(
                permission_acl_edit, permission_acl_view
            )
        )

        SourceColumn(
            attribute='datetime', is_identifier=True, include_label=True,
            is_sortable=True,
            source=DownloadFile
        )
        SourceColumn(
            attribute='label', include_label=True, is_sortable=True,
            source=DownloadFile
        )
        SourceColumn(
            attribute='content_object', include_label=True,
            label=_('Source object'), source=DownloadFile,
            is_attribute_absolute_url=True,
        )
        SourceColumn(
            attribute='filename', include_label=True, is_sortable=True,
            source=DownloadFile
        )

        menu_object.bind_links(
            links=(
                link_download_file_delete, link_download_file_download,
            ), sources=(DownloadFile,)
        )
        menu_tools.bind_links(links=(link_download_file_list,))
