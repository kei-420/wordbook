from django.urls import path, re_path
from wordbook.views import quiz, wordbook


app_name = 'wordbook'
urlpatterns = [
    path('home/', wordbook.HomeView.as_view(), name='home'),
    path('home/add_word/', wordbook.WordAddView.as_view(), name='add_word'),
    path('home/delete_word/<int:pk>/', wordbook.WordDeleteView.as_view(), name='delete_word'),
    path('home/quiz_list/', quiz.QuizListView.as_view(), name='quiz_list'),
    path('home/completed_quiz_list/', quiz.CompletedQuizListView.as_view(), name='completed_quiz_list'),
    path('home/quiz_list/quiz_add/', quiz.QuizCreateView.as_view(), name='quiz_add'),
    path('home/quiz_list/game_delete/<int:pk>/', quiz.QuizDeleteView.as_view(), name='quiz_delete'),
    path('home/quiz_list/quiz/<int:pk>/take/', quiz.take_quiz, name='quiz_take'),
    path('home/completed_quiz_list/<int:pk>/delete', quiz.CompletedQuizDeleteView.as_view(), name='completed_quiz_delete')
]
