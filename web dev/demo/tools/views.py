from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Upload
from .forms import UploadsForm
import mimetypes


class UploadsView(CreateView):

    model = Upload
    form_class = UploadsForm
    template_name = 'tools/upload.html'
    success_url = reverse_lazy('home')


class DownloadsView(ListView):

    model = Upload
    template_name = 'tools/documents.html'
    context_object_name = 'images'


def download(request, image_id):
    """ download view """
    document = get_object_or_404(Upload, pk=image_id)
    file_name = document.image.name
    mime_type, _ = mimetypes.guess_type(file_name)
    file_size = document.image.size

    response = HttpResponse(document.image, content_type=mime_type)
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    response['Content-Length'] = file_size
    return response
