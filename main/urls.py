from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'main'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('articles/<int:post_id>', views.articles, name='articles'),
    path('categories/<int:category_id>', views.index, name='categories'),
    path('authors/<int:author_id>', views.authors, name='authors'),
    path('about/', views.about, name='about'),
    path('ajax/get-title', views.get_title, name='get-title'),
    path('ajax/update-cvs', views.update_cvs, name='update-cvs'),
    path('secret/', views.secret_articles, name='secret'),
    path('activate/', views.activate, name='activate'),
    path('tinymce/upload/', views.tinymce_upload_image, name='tinymce-upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
