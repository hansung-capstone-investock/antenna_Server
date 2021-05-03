from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from scraping import views
from rest_framework import routers


urlpatterns = [
    path('dc/', views.parse_dc),
    path('fmkor/', views.parse_fmkor),
    path('company/', views.company_list),
    path('mainnews/',views.crawlerNews),
    url(r'api/news/$', views.mainnews_list),
    path('api/dcList/', views.dc_list),
    path('api/companyList/', views.company_list),
    path('api/fmkorList/', views.fmkor_list),
]
