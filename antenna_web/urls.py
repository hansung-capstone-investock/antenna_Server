from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('views/', include('scraping.urls')),
    # path('fmkor/', include('scraping.urls')),
]
