from django.urls import path, include
from django.contrib import admin
from django.shortcuts import render


urlpatterns = [
    path('', include('main.urls')),
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
]


def custom_handler404(request, exception=None):
    response = render(request, 'main/404.html')
    response.status_code = 404
    return response
handler404 = custom_handler404

def custom_handler500(request):
    response = render(request, 'main/500.html')
    response.status_code = 500
    return response
handler500 = custom_handler500
