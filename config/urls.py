from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from collaboration import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('collaboration/', include('collaboration.urls')),
    path('forum/', include('forum.urls')),
    path('', views.index, name='index'),
]

# 개발 모드에서 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

