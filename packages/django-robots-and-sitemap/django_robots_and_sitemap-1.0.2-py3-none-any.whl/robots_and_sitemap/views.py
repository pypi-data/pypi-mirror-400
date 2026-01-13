import requests
from django.http import Http404, HttpResponse
from django.urls import reverse
from . import ROBOTS_PATH, SITEMAP_PATH
from .decorators import file_exists


@file_exists(ROBOTS_PATH)
def robots(request):
    with open(ROBOTS_PATH, encoding="utf-8") as file:
        text = file.read()
        if 'Sitemap' not in text:
            url = request.build_absolute_uri(reverse('sitemap'))
            if requests.get(url).ok:
                text += '\n\n' + url
        return HttpResponse(text, content_type="text/plain")



@file_exists(SITEMAP_PATH)
def sitemap(request=None):
    return HttpResponse(SITEMAP_PATH.read_text('utf-8'), content_type="text/xml")
