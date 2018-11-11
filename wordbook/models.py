import json
import numpy as np

import random

from django.db import models
from accounts.models import UserManager
from django.db import connection
from django.utils.encoding import python_2_unicode_compatible

from django.core.exceptions import ValidationError, ImproperlyConfigured
from model_utils.managers import InheritanceManager


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


# class GameListManager(models.Manager):
#     def create_question_list(self, user):
#         user_word_data = Wordbook.objects.filter(user=user)
#         is_randomly_selected = np.random.choice(list(user_word_data.values('word__vocab', 'word__vocab_meaning')),
#                                                 user_word_data.count(), replace=False
#                                                 )
#         for i in list(is_randomly_selected):
#             is_game_word = i['word__vocab']
#             is_answer = i['word__vocab_meaning']
#             choices = Word.objects.exclude(vocab_meaning=is_answer).values('vocab_meaning')
#             three_other_choices = np.random.choice(list(choices), 3, replace=False)
#             appended_choices = list(three_other_choices).append(is_answer)
#             random.shuffle(appended_choices)
#             question_list = self.create(user=user,
#                                         game_word=is_game_word,
#                                         choices=appended_choices,
#                                         answer=is_answer,
#                                         )
#             return question_list


# class PracticeGameManager(models.Manager):
#     def new_game(self, user, game):
#         question_set = game.gameword_set.all().select_subclasses
#         question_set = [item.id for item in question_set]
#         if len(question_set) == 0:
#             raise ImproperlyConfigured('Question set is empty. '
#                                        'Please make sure that you have at least one word in your wordbook.')
#         questions = ",".join(map(str, question_set)) + ","
#         new_game = self.create(user=user,
#                                game=game,
#                                question_order=questions,
#                                question_list=questions,
#                                incorrect_questions="",
#                                score=0,
#                                user_answers='{}',
#                                )
#         return new_game
#
#     def user_progress(self, user, game):
#         if self.filter(user=user, game=game):
#             return False
#         try:
#             progress = self.get(user=user, game=game)
#         except PracticeGame.DoesNotExist:
#             progress = self.new_game(user, game)
#         except PracticeGame.MultipleObjectsReturned:
#             progress = self.filter(user=user, game=game)
#         return progress
#
#
# class PracticeGame(models.Model):
#     user = models.ForeignKey(UserManager, on_delete=models.PROTECT)
#     question_order = models.CommaSeparatedIntegerField(max_length=1024)
#     question_list = models.CommaSeparatedIntegerField(max_length=1024)
#     incorrect_questions = models.CommaSeparatedIntegerField(max_length=1024)
#     score = models.IntegerField()
#     user_answers = models.TextField(blank=True, default='{}')
#     objects = PracticeGameManager()
#
#     def get_questions(self):
#         return self.gameword_set.all().select_subclasses
#
#     @property
#     def get_max_score(self):
#         return self.get_questions().count()
#
#
# class GameWord(models.Model):
#     gameword = models.ForeignKey(Wordbook, on_delete=models.PROTECT)
#     practice_game = models.ManyToManyField(PracticeGame, blank=True)
#
#     objects = InheritanceManager()