from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
from django.http.request import QueryDict

# Create your views here.


def index(request: WSGIRequest):
    """ home view """
    return render(request, "tools/index.html")


def make_thumbnail(request: WSGIRequest):
    """ thumbnail view """
    if request.method == "POST":
        images = request.POST.getlist("images")
        print("--> Thumbnail:", images)
    # else
    return render(request, "tools/thumbnail.html")


def invert_BW(request: WSGIRequest):
    """ invert color palette, black to white and vice versa """
    if request.method == "POST":
        images = request.POST.getlist("images")
        print("--> iColor:", images)
    # else
    return render(request, "tools/invertcolor.html")
