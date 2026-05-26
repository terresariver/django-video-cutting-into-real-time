from django.urls import path
from .views import export_download, export_status, upload_video, process_video,test_process,export_video,test_export,process_status

urlpatterns = [
    path('video/upload/',upload_video),
    path('video/processing/', process_video),
    path('video/export/', export_video),
    path('test/process/',test_process),
    path('test/export/',test_export),
    path("video/export/",export_video),
    path("video/export/status/<task_id>/",export_status),
    path("video/processing/status/<video_id>/",process_status),
    path("video/export/download/<task_id>/",export_download),
]