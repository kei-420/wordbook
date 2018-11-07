from django.urls import path
from . import views


app_name = 'wordbook'
urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('home/add_word/', views.WordAddView.as_view(), name='add_word'),
    path('home/delete_word/<int:pk>/', views.WordDeleteView.as_view(), name='delete_word'),
    path('home/repeated_game/', views.RepeatedGameView.as_view(), name='repeated_game'),
]
