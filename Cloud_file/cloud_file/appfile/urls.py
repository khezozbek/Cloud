from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_cloud, name='create_cloud'),
    path('server/<int:server_id>/', views.cloud_detail, name='cloud_detail'),
    path('server/<int:server_id>/upload/', views.upload_file, name='upload_file'),
    path('server/<int:file_id>/download/', views.download_file, name='download_file'),
    path('delete/<int:server_id>/', views.delete_server, name='delete_server'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='html/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('file/<int:file_id>/transfer/', views.file_transfer, name='file_transfer'),
]