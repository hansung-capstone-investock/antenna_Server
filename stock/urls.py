from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from stock import views
from rest_framework import routers


urlpatterns = [
    path('marketlist/',views.marketList),
    path('kospiyear/',views.kospiYearList),
    path('kosdaqyear/',views.kosdaqYearList),
    path('kospi200year/',views.kospi200YearList),
    path('bt/',views.backtestapi),
    path('btApp/',views.backAppapi),
    path('stocksearch/', views.stockSearchData),
    path('compare3/',views.before3M),
    path('topstock/',views.topStock),
    path('backtestlog/',views.backtestLogData),
]