from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="tools-index"),
    path("thumbnail/", views.make_thumbnail, name="tools-thumbnail"),
    path("color/", views.invert_BW, name="tools-color"),

]
