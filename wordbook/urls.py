from django.urls import path, re_path
from . import views


app_name = 'wordbook'
urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('home/add_word/', views.WordAddView.as_view(), name='add_word'),
    path('home/delete_word/<int:pk>/', views.WordDeleteView.as_view(), name='delete_word'),
    path('home/game_list/', views.PracticeGameListView.as_view(), name='game_list'),
    path('home/game_add/', views.PracticeGameAddView.as_view(), name='game_add'),
    path(r'^home/game_list/(?P<slug>[\w-]+)/$', views.PracticeGameDetailView.as_view(), name='game_detail'),
    path('home/game/(?P<practicegame_name>[\w-]+)/take/$', views.PracticeGamePlayView.as_view(), name='game_play'),
]
