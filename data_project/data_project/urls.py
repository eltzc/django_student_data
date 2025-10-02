from django.contrib import admin
from django.urls import path, include # <- Убедитесь, что 'include' импортирован

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Подключаем все URL-адреса из data_app и начинаем их с пустой строки (т.е. с корня сайта)
    path('', include('data_app.urls')), 
]