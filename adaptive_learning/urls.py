from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

handler404 = 'learning.views.error_404'
handler500 = 'learning.views.error_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('learning.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
