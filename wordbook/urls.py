from django.urls import path, re_path
from . import views


app_name = 'wordbook'
urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('home/add_word/', views.WordAddView.as_view(), name='add_word'),
    path('home/delete_word/<int:pk>/', views.WordDeleteView.as_view(), name='delete_word'),
    path('home/game_list/', views.PracticeGameListView.as_view(), name='game_list'),
    path('home/game_add/', views.PracticeGameAddView.as_view(), name='game_add'),
    re_path(r'^home/game_list/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<slug>[\w-]+)/$',
            views.PracticeGameDetailView.as_view(), name='game_detail'),
    path('home/game/?P<slug>[\w-]+', views.PracticeGamePlayView.as_view(), name='game_play'),
]
