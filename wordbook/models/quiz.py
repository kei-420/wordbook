from django.db import models

from accounts.models import UserManager
from wordbook.models.wordbook import Word


class QuizLength(models.Model):
    length = models.IntegerField()

    def __str__(self):
        return str(self.length)


class Quiz(models.Model):
    taker = models.ForeignKey(UserManager, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)
    length = models.ForeignKey(QuizLength, on_delete=models.PROTECT, related_name='quizzes')

    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    game_word = models.ForeignKey(Word, on_delete=models.CASCADE)


class MultipleQuestions(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    # choices = models.ForeignKey(Word, on_delete=models.PROTECT, related_name='choices')
    meaning = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct Answer', default=False)
    # is_user_choice = models.BooleanField('User Choice', default=False)

    def __str__(self):
        return self.meaning


class QuizTaker(models.Model):
    user = models.OneToOneField(UserManager, on_delete=models.CASCADE, primary_key=True)
    quizzes = models.ManyToManyField(Quiz, through='CompletedQuiz')

    def get_unanswered_questions(self, quiz):
        answered_questions = self.quiz_answers.filter(answer__question__quiz=quiz).values_list('answer__question__pk', flat=True)
        questions = quiz.questions.exclude(pk__in=answered_questions).order_by('answers')
        return questions

    def __str__(self):
        return self.user.username


class CompletedQuiz(models.Model):
    user = models.ForeignKey(QuizTaker, on_delete=models.CASCADE, related_name='completed_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='completed_quizzes')
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)


class QuizTakerAnswer(models.Model):
    taker = models.ForeignKey(QuizTaker, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.ForeignKey(MultipleQuestions, on_delete=models.CASCADE, related_name='+')



