from django.urls import path
from .views import (
    export_download, export_status, upload_video, process_video, test_process,
    export_video, test_export, process_status, upload_watermark, generate_reels,
    register, login, logout, test_login, test_logout, export_clip, clip_export_status,
    clip_export_download
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    #auth
    path('auth/register/', register),
    path('auth/login/', login),
    path('auth/logout/', logout),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    path('test/login/', test_login),
    path('test/logout/', test_logout),

    #video operations
    path('video/upload/', upload_video),
    path('video/processing/', process_video),
    path('video/export/', export_video),
    path('test/process/', test_process),
    path('test/export/', test_export),
    path('video/export/status/<task_id>/', export_status),
    path('video/processing/status/<video_id>/', process_status),
    path('video/export/download/<task_id>/', export_download),
    path('watermark/upload/', upload_watermark),
    path('video/reel/', generate_reels),

    #clip operations
    path('clip/export/', export_clip),
    path('clip/export/status/<task_id>/', clip_export_status),
    path('clip/export/download/<task_id>/', clip_export_download),
]