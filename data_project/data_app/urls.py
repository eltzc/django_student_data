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

    path('ajax/search-students/', views.ajax_search_students, name='ajax_search_students'),

    path('student/<int:id>/update/', views.student_data_update, name='student_data_update'),

    path('student/<int:id>/delete/', views.student_data_delete, name='student_data_delete'),

    path('display_all_files/', views.display_all_files, name='display_all_files'),
]