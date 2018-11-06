# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from accounts.models import UserManager


class WordMeanings(models.Model):
    class Meta:
        db_table = 'word_meanings'

    wordid = models.CharField(max_length=255)
    vocab_meaning = models.TextField()
    lang = models.CharField(max_length=10)

    def __str__(self):
        return str(self.wordid) + ' | ' + str(self.vocab_meaning)


class Word(models.Model):
    class Meta:
        db_table = 'word'

    wordid = models.CharField(max_length=255)
    vocab = models.CharField(max_length=255)
    vocab_class = models.CharField(max_length=20)
    vocab_meaning = models.ForeignKey(WordMeanings, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.vocab


class Wordbook(models.Model):
    class Meta:
        db_table = 'wordbook'

    user = models.ForeignKey(UserManager, on_delete=models.PROTECT)
    word = models.ForeignKey(Word, on_delete=models.PROTECT)
    adding_word = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.adding_word


# class RepeatedGame(models.Model):
#     class Meta:
#         db_table = 'repeated_game'
#
#     user = models.ForeignKey(
#         Wordbook,
#         on_delete=models.PROTECT,
#     )
#     trials = models.PositiveIntegerField(
#         default=0,
#     )
#
#     def __str__(self):
#         return self.user


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