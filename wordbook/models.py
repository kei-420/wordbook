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


class PracticeGameContext(models.Model):
    user = models.ForeignKey(UserManager, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)


class Question(models.Model):
    wordbook = models.ForeignKey(Wordbook, on_delete=models.PROTECT)
    practice_game = models.ForeignKey(PracticeGameContext, on_delete=models.PROTECT)
    was_correct = models.BooleanField(default=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


class MultipleChoices(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    word = models.ForeignKey(Word, on_delete=models.PROTECT)





























