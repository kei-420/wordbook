from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('selvoc/accounts/', include('accounts.urls')),
    path('selvoc/wordbook/', include('wordbook.urls')),
]
