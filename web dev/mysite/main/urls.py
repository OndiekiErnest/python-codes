from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="main-index"),
    path("<int:list_id>", views.get, name="main-get"),
    path("create/", views.create, name="main-create"),
    path("todolists/", views.todolists, name="main-todolists"),

]
