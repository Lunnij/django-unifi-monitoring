from django.urls import path
from logger import views


urlpatterns = [
    path('', views.index, name='logger'),
    path('log', views.log, name='log'),
    path('stop', views.stop_log, name='log-stop')
]