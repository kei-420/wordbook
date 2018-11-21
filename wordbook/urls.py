from django.urls import path, re_path
from wordbook.views import practicegame, wordbook


app_name = 'wordbook'
urlpatterns = [
    path('home/', wordbook.HomeView.as_view(), name='home'),
    path('home/add_word/', wordbook.WordAddView.as_view(), name='add_word'),
    path('home/delete_word/<int:pk>/', wordbook.WordDeleteView.as_view(), name='delete_word'),
    path('home/quiz_list/', practicegame.QuizListView.as_view(), name='quiz_list'),
    path('home/completed_quiz_list/', practicegame.CompletedQuizListView.as_view(), name='completed_quiz_list'),
    path('home/quiz_list/quiz_add/', practicegame.QuizCreateView.as_view(), name='quiz_add'),
    path('home/quiz_list/game_delete/<int:pk>/', practicegame.QuizDeleteView.as_view(), name='quiz_delete'),
    # path(r'^home/game_list/(?P<slug>[\w-]+)/$', practicegame.PracticeGameDetailView.as_view(), name='game_detail'),
    path('home/quiz_list/quiz/<int:pk>/take/', practicegame.take_quiz, name='quiz_take'),
]
