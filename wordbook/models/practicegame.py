from django.db import models, connection

from django.core.exceptions import ImproperlyConfigured
from django.core.validators import validate_comma_separated_integer_list

from accounts.models import UserManager
from wordbook.models.wordbook import Wordbook, Word


class PracticeGame(models.Model):
    """
    title: automatically created in a japanese date format by 'created_at'.
           Displayed on the PracticeGameListView(views.py)

    url: automatically created once a user accesses to web page.

    random_order: Display the questions in a random order or as they are set?

    max_questions: Number of questions to be answered on each attempt.

    answers_at_end: Correct answer is NOT shown after question as default=False.

    exam_paper: If yes(True), the result of each attempt by a user will be stored. Necessary for making.

    single_attempt: If yes(True), only one attempt by a user will be permitted. Non users cannot sit this exam.

    """
    title = models.CharField(max_length=60, blank=False)

    user = models.ForeignKey(UserManager, on_delete=models.PROTECT)

    url = models.SlugField(max_length=60, blank=False)

    single_attempt = models.BooleanField(blank=False, default=False)

    complete = models.BooleanField(blank=False, default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'practicegame'

    def __str__(self):
        return self.title


class Question(models.Model):
    """Question is used for making 10 questions per 'practice_game'
        and for measuring whether each answer per question is correct"""
    practice_game = models.ForeignKey(PracticeGame, blank=True, on_delete=models.PROTECT)
    wordbook = models.ForeignKey(Wordbook, on_delete=models.PROTECT)
    # practice_game_context = models.ForeignKey(PracticeGameContext, on_delete=models.PROTECT)

    was_correct = models.BooleanField(default=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'question'


class MultipleChoices(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    word = models.ForeignKey(Word, on_delete=models.PROTECT)

    @staticmethod
    def exec_query(question_id):
        with connection.cursor() as cur:
            sqltext = """
            SELECT word.vocab_meaning, wordbook_multiplechoices.question_id
            FROM word INNER JOIN wordbook_multiplechoices ON word.id=wordbook_multiplechoices.word_id
            WHERE question_id = %s
            """ % question_id
            cur.execute(sqltext)
            columns = [col[0] for col in cur.description]
            show_list = [dict(zip(columns, row)) for row in cur.fetchall()]
            return show_list

    @staticmethod
    def exec_query2(question_id):
        with connection.cursor() as cur:
            sqltext = """
            select wordbook.word_id
            from wordbook inner join wordbook_question
            on wordbook.id = wordbook_question.wordbook_id
            where wordbook_question.id = %s
            """ % question_id
            cur.execute(sqltext)
            columns = [col[0] for col in cur.description]
            show_list = [dict(zip(columns, row)) for row in cur.fetchall()]
            return show_list

    class Meta:
        db_table = 'multiplechoices'


class UserProgress(models.Model):
    """
    PracticeGameContext is used for storing 'practice_game' created by each user and for tracking its scores.
    """
    # user = models.ForeignKey(UserManager, on_delete=models.PROTECT)
    practice_game = models.ForeignKey(PracticeGame, on_delete=models.PROTECT)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_score(self):
        return self.score

    def get_score_percentage(self):
        return str(self.score / 10 * 100) + '%'

    class Meta:
        db_table = 'practicegamecontext'

    def __str__(self):
        return str(self.practice_game) + '| ' + str(self.score)


class UserAnswer(models.Model):
    user = models.ForeignKey(UserManager, on_delete=models.PROTECT)
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return str(self.user) + '| ' + str(self.question)


class CompletedPracticeGame(models.Model):
    user_progress = models.ForeignKey(UserProgress, on_delete=models.CASCADE)
    game = models.ForeignKey(PracticeGame, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    @property
    def get_score(self):
        return self.score

    @property
    def get_score_percentange(self):
        return self.score / 10

