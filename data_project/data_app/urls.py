from django.urls import path
from . import views

urlpatterns = [
    # URL для отображения формы и сохранения данных
    path('new/', views.student_data_create, name='student_data_create'),
    
    # URL для отображения списка (пока пустой)
    path('', views.student_data_list, name='student_data_list'),
]