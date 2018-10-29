from django.db import models
from accounts.models import UserManager
from simple_history.models import HistoricalRecords
import numpy as np


class Word(models.Model):
    class Meta:
        db_table = 'word'

    vocab = models.CharField(
        max_length=255,
    )
    vocab_class = models.CharField(
        max_length=20,
        blank=True,
    )
    vocab_meaning = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return str(self.id) + ' | ' + str(self.vocab)


class Wordbook(models.Model):
    class Meta:
        db_table = 'wordbook'

    user = models.ForeignKey(
        UserManager,
        on_delete=models.PROTECT,
    )
    word = models.ForeignKey(
        Word,
        on_delete=models.PROTECT,
    )
    adding_word = models.CharField(
        max_length=255,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # def __init__(self, word, user, *args, **kwargs):
    #     super(Wordbook, self).__init__(self, *args, **kwargs)
    #     self.word = word
    #     self.user = user

    def __str__(self):
        return str(self.adding_word)


class RepeatedGame(models.Model):
    class Meta:
        db_table = 'repeated_game'

    user = models.ForeignKey(
        Wordbook,
        on_delete=models.PROTECT,
    )
    trials = models.PositiveIntegerField(
        default=0,
    )

    def __str__(self):
        return self.user


# class WordForGame(models.Model):


# class History(models.Model):
#     class Meta:
#         db_table = 'history'
#
#     user = models.ForeignKey(
#         UserManager,
#         on_delete=models.PROTECT,
#     )
#     history = HistoricalRecords()

