from django.urls import path
from . import views

urlpatterns = [
    # URL для отображения формы и сохранения данных
    path('new/', views.student_data_create, name='student_data_create'),

    # URL для отображения списка (пока пустой)
    path('', views.student_data_list, name='student_data_list'),

    # URL для загрузки файла
    path('upload/', views.upload_file, name='upload_file'),

    # URL для отображения содержимого файла
    path('display/', views.display_file, name='display_file'),

    path('export/<str:format>/', views.export_data, name='export_data'),
]