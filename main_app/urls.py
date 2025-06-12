from django.urls import path
from . import views 

urlpatterns = [
 
    path('', views.dashboard, name='dashboard'),
    path('data-analysis/', views.data_analysis, name='data_analysis'),
    path('data-converter/', views.data_converter, name='data_converter'),
    path('data-scraping/', views.data_scraping, name='data_scraping'),
    path('projects/', views.projects, name='projects'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register_user, name='register_user'), 
    path('profile/', views.profile, name='profile'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('download-scraped-data/', views.download_scraped_data, name='download_scraped_data'),
]