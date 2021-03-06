from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from scraping import views
from rest_framework import routers


urlpatterns = [
    path('dc/', views.parse_dc),
    path('mainnews/',views.crawlerNews),
    path('livenews/',views.liveNews),
    url(r'api/news/$', views.mainnews_list),
    path('api/livenews/', views.livenews_list),
    path('api/dcList/', views.dc_list),
]
