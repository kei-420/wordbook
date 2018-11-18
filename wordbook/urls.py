from django.urls import path, re_path
from wordbook.views import practicegame, wordbook


app_name = 'wordbook'
urlpatterns = [
    path('home/', wordbook.HomeView.as_view(), name='home'),
    path('home/add_word/', wordbook.WordAddView.as_view(), name='add_word'),
    path('home/delete_word/<int:pk>/', wordbook.WordDeleteView.as_view(), name='delete_word'),
    path('home/game_list/', practicegame.PracticeGameListView.as_view(), name='game_list'),
    path('home/game_add/', practicegame.PracticeGameAddView.as_view(), name='game_add'),
    path('home/game_delete/<int:pk>/', practicegame.PracticeGameDeleteView.as_view(), name='game_delete'),
    path(r'^home/game_list/(?P<slug>[\w-]+)/$', practicegame.PracticeGameDetailView.as_view(), name='game_detail'),
    # path('home/game/(?P<practicegame_name>[\w-]+)/take/$', practicegame.PracticeGamePlayView.as_view(), name='game_play'),
]
