"""
Admin URLs for database backup functionality
These URLs are included in the main urls.py before admin.site.urls
"""
from django.urls import path
from . import admin_views

urlpatterns = [
    path('admin/backup-database/', admin_views.backup_database, name='admin_backup_database'),
    path('admin/backup-download/<str:filename>/', admin_views.download_backup, name='admin_backup_download'),
    path('admin/backup-cleanup/', admin_views.cleanup_backups, name='admin_backup_cleanup'),
]
