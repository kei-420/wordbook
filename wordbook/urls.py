from django.urls import path
from . import views


app_name = 'wordbook'
urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('home/add_word', views.WordAddView.as_view(), name='add_word'),
]