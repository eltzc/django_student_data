from django.contrib import admin
from django.urls import path, include # <- Убедитесь, что 'include' импортирован
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Подключаем все URL-адреса из data_app и начинаем их с пустой строки (т.е. с корня сайта)
    path('', include('data_app.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)