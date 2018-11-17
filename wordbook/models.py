import re
import json
from datetime import datetime as dt
import numpy as np

import random

from django.db import models
from accounts.models import UserManager
from django.db import connection
from django.utils.encoding import python_2_unicode_compatible

from django.core.exceptions import ValidationError, ImproperlyConfigured
from model_utils.managers import InheritanceManager
from django.core.validators import MaxValueValidator, validate_comma_separated_integer_list


class Word(models.Model):
    class Meta:
        db_table = 'word'

    # wordid = models.CharField(max_length=255)
    vocab = models.CharField(max_length=255)
    vocab_class = models.CharField(max_length=20)
    vocab_meaning = models.TextField()

    def __str__(self):
        return self.vocab


class Wordbook(models.Model):
    class Meta:
        db_table = 'wordbook'

    user = models.ForeignKey(UserManager, on_delete=models.PROTECT)
    word = models.ForeignKey(Word, on_delete=models.PROTECT)
    # word_meaning = models.ForeignKey(WordMeanings, on_delete=models.PROTECT)
    adding_word = models.CharField(max_length=255)
    understanding_level = models.PositiveIntegerField(blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.adding_word

    @staticmethod
    def exec_query(user):
        with connection.cursor() as cur:
            sqltext = """
            SELECT wordbook.id, word.vocab, word.vocab_class, word.vocab_meaning 
            FROM wordbook LEFT OUTER JOIN word 
            ON wordbook.word_id = word.id 
            WHERE user_id = %s""" % user
            cur.execute(sqltext)
            columns = [col[0] for col in cur.description]
            show_list = [dict(zip(columns, row)) for row in cur.fetchall()]
            return show_list


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

    random_order = models.BooleanField(blank=False, default=False)

    max_questions = models.PositiveIntegerField(blank=True, null=True)

    answers_at_end = models.BooleanField(blank=False, default=False)

    exam_paper = models.BooleanField(blank=False, default=False)

    single_attempt = models.BooleanField(blank=False, default=False)

    draft = models.BooleanField(blank=True, default=False,)

    created_at = models.DateTimeField(auto_now_add=True)

    # def save(self, force_insert=False, force_update=False, *args, **kwargs):
    #     """Customizing and Overriding save method."""
    #     self.url = re.sub('\s+', '-', self.url).lower()
    #
    #     self.url = ''.join(letter for letter in self.url if letter.isalnum() or letter == '-')
    #
    #     pattern = re.compile(' [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{1,20}')
    #     if self.created_at:
    #         eng_date = '%s' % pattern.sub('', str(self.created_at))
    #         split_date = eng_date.split('-')
    #         joining_as_jap_date = '{0}年{1}月{2}日'.format(split_date[0], split_date[1], split_date[2])
    #         self.title = joining_as_jap_date
    #
    #     if self.single_attempt is True:
    #         self.exam_paper = True
    #
    #     super(PracticeGame, self).save(force_insert, force_update, *args, **kwargs)

    class Meta:
        db_table = 'practicegame'

    def __str__(self):
        return self.title

    def get_questions(self):
        return self.question_set.all().select_subclasses()

    @property
    def get_max_score(self):
        return self.get_questions().count()

    def anon_score_id(self):
        return str(self.id) + "_score"

    def anon_q_list(self):
        return str(self.id) + '_q_list'

    def anon_q_data(self):
        return str(self.id) + '_data'


class PracticeGameContextManager(models.Manager):
    def new_game_context(self, user):
        new_game_context = self.create(user=user, score="")

        new_game_context.save()
        return new_game_context


class PracticeGameContext(models.Model):
    """
    PracticeGameContext is used for storing 'practice_game' created by each user and for tracking its scores.
    """
    # user = models.ForeignKey(UserManager, on_delete=models.PROTECT)
    practice_game = models.ForeignKey(PracticeGame, on_delete=models.PROTECT)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PracticeGameContextManager()

    @property
    def get_score(self):
        return self.score

    def get_score_percentage(self):
        return str(self.score / 10 * 100) + '%'

    class Meta:
        db_table = 'practicegamecontext'


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


class SittingManager(models.Manager):

    def new_sitting(self, user, quiz):
        if quiz.random_order is True:
            question_set = quiz.question_set.all().select_subclasses().order_by('?')
        else:
            question_set = quiz.question_set.all().select_subclasses()

        question_set = [item.id for item in question_set]

        if len(question_set) == 0:
            raise ImproperlyConfigured('Question set of the quiz is empty. '
                                       'Please configure questions properly')

        if quiz.max_questions and quiz.max_questions < len(question_set):
            question_set = question_set[:quiz.max_questions]

        questions = ",".join(map(str, question_set)) + ","

        new_sitting = self.create(user=user,
                                  quiz=quiz,
                                  question_order=questions,
                                  question_list=questions,
                                  incorrect_questions="",
                                  current_score=0,
                                  complete=False,
                                  user_answers='{}')
        return new_sitting

    def user_sitting(self, user, quiz):
        if quiz.single_attempt is True and self.filter(user=user,
                                                       quiz=quiz,
                                                       complete=True).exists():
            return False

        try:
            sitting = self.get(user=user, quiz=quiz, complete=False)
        except Sitting.DoesNotExist:
            sitting = self.new_sitting(user, quiz)
        except Sitting.MultipleObjectsReturned:
            sitting = self.filter(user=user, quiz=quiz, complete=False)[0]
        return sitting


class Sitting(models.Model):
    """
    Sitting performs practice game per user request
    Used to store the progress of logged in users sitting a quiz.
    Replaces the session system used by anon users.

    Question_order is a list of integer pks of all the questions in the
    quiz, in order.

    Question_list is a list of integers which represent id's of
    the unanswered questions in csv format.

    Incorrect_questions is a list in the same format.

    Sitting is deleted when quiz is finished unless quiz.exam_paper is true.

    User_answers is a json object in which the question PK is stored
    with the answer the user gave.
    """

    # user = models.ForeignKey(UserManager, on_delete=models.PROTECT)

    practice_game = models.ForeignKey(PracticeGame, on_delete=models.PROTECT)

    question_order = models.CharField(validators=[validate_comma_separated_integer_list], max_length=1024)

    question_list = models.CharField(validators=[validate_comma_separated_integer_list], max_length=1024)

    incorrect_questions = models.CharField(validators=[validate_comma_separated_integer_list], max_length=1024)

    current_score = models.IntegerField()

    complete = models.BooleanField(default=False, blank=False)

    user_answers = models.TextField(blank=True, default='{}')

    start = models.DateTimeField(auto_now_add=True)

    end = models.DateTimeField(null=True, blank=True)

    objects = SittingManager()

    class Meta:
        db_table = 'sitting'

    def get_first_question(self):
        """
        Returns the next question.
        If no question is found, returns False
        Does NOT remove the question from the front of the list.
        """
        if not self.question_list:
            return False

        first, _ = self.question_list.split(',', 1)
        question_id = int(first)
        return Question.objects.get_subclass(id=question_id)

    def remove_first_question(self):
        if not self.question_list:
            return

        _, others = self.question_list.split(',', 1)
        self.question_list = others
        self.save()

    def add_to_score(self, points):
        self.current_score += int(points)
        self.save()

    @property
    def get_current_score(self):
        return self.current_score

    def _question_ids(self):
        return [int(n) for n in self.question_order.split(',') if n]

    @property
    def get_percent_correct(self):
        dividend = float(self.current_score)
        divisor = len(self._question_ids())
        if divisor < 1:
            return 0            # prevent divide by zero error

        if dividend > divisor:
            return 100

        correct = int(round((dividend / divisor) * 100))

        if correct >= 1:
            return correct
        else:
            return 0

    def mark_quiz_complete(self):
        self.complete = True
        self.end = dt.now()
        self.save()

    def add_incorrect_question(self, question):
        """
        Adds uid of incorrect question to the list.
        The question object must be passed in.
        """
        if len(self.incorrect_questions) > 0:
            self.incorrect_questions += ','
        self.incorrect_questions += str(question.id) + ","
        if self.complete:
            self.add_to_score(-1)
        self.save()

    @property
    def get_incorrect_questions(self):
        """
        Returns a list of non empty integers, representing the pk of
        questions
        """
        return [int(q) for q in self.incorrect_questions.split(',') if q]

    def remove_incorrect_question(self, question):
        current = self.get_incorrect_questions
        current.remove(question.id)
        self.incorrect_questions = ','.join(map(str, current))
        self.add_to_score(1)
        self.save()

    def add_user_answer(self, question, guess):
        current = json.loads(self.user_answers)
        current[question.id] = guess
        self.user_answers = json.dumps(current)
        self.save()

    def get_questions(self, with_answers=False):
        question_ids = self._question_ids()
        questions = sorted(
            self.practice_game.question_set.filter(id__in=question_ids).select_subclasses(),
            key=lambda q: question_ids.index(q.id))

        if with_answers:
            user_answers = json.loads(self.user_answers)
            for question in questions:
                question.user_answer = user_answers[str(question.id)]

        return questions

    @property
    def questions_with_user_answers(self):
        return {
            q: q.user_answer for q in self.get_questions(with_answers=True)
        }

    @property
    def get_max_score(self):
        return len(self._question_ids())

    def progress(self):
        """
        Returns the number of questions answered so far and the total number of
        questions.
        """
        answered = len(json.loads(self.user_answers))
        total = self.get_max_score
        return answered, total

