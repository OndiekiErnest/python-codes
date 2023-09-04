from django.urls import path
from .views import UploadsView, DownloadsView, download

urlpatterns = [
    path('', DownloadsView.as_view(), name='home'),
    path('upload/', UploadsView.as_view(), name='upload'),
    path('download/<int:image_id>/', download, name='download'),
]
