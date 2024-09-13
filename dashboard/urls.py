from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('dashboard/', views.dashboard,  name='dashboard'),
  path('login/', views.user_login, name='user_login'),
  path('create_account/', views.create_account, name='create_account'),
  path('logout/', views.user_logout, name='user_logout'),
  path('profile/', views.view_profile, name='view_profile'),
  path('youtube/', views.youtube, name='youtube'),
  path('news/', views.news, name='news'),
  path('store-news/', views.store_news, name='store_news'),
  path('admin_view_ministry/', views.admin_view_ministry, name='admin_view_ministry'),
  path('404/', views.custom_404, name='custom_404'),
]

handler404 = 'dashboard.views.custom_404'
