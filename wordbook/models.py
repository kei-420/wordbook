from django.db import models
from accounts.models import UserManager
from django.db import connection
from django.utils.encoding import python_2_unicode_compatible


# class WordMeanings(models.Model):
#     class Meta:
#         db_table = 'word_meanings'
#
#     wordid = models.CharField(max_length=255)
#     vocab_meaning = models.TextField()
#     lang = models.CharField(max_length=10)
#
#     def __str__(self):
#         return str(self.wordid) + ' | ' + str(self.vocab_meaning)
#

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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.adding_word

    # @staticmethod
    # def exec_query(user):
    #     with connection.cursor() as cur:
    #         sqltext = """
    #                 SELECT vocab, vocab_class, vocab_meaning, wordbook.id FROM word
    #                 INNER JOIN wordbook ON word.id = wordbook.word_id
    #                 INNER JOIN word_meanings ON word.wordid = word_meanings.wordid
    #                 WHERE word_meanings.lang='jpn' and wordbook.user_id=%s
    #                 """ % user
    #         cur.execute(sqltext)
    #         columns = [col[0] for col in cur.description]
    #         show_list = [dict(zip(columns, row)) for row in cur.fetchall()]
    #         return show_list
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
# class Practice(models.Model):
#     class Meta:
#         db_table = 'practice'
#
#     user = models.ForeignKey(UserManager, on_delete=models.PROTECT)
#     trial = models.IntegerField()
#
#     def __init__(s    elf, trial):
#         super(Practice, self).__init__(trial)
#         self.trial = trial
#
#     def increment_trials(self, user):
#         if user:
#             self.trial += 1
#
#
# class Choices(models.Model):
#     game_word = models.ForeignKey(Wordbook, on_delete=models.PROTECT)
#     choice = models.C
#     class Meta:
#         db_table = 'choices'
#         unique_together = [
#
#         ]


# class Practice(models.Model):
#     game_word = models.ForeignKey(Wordbook, on_delete=models.PROTECT)
#     # player = models.ForeignKey(UserManager, on_delete=models.PROTECT)
#     random_order = models.BooleanField(blank=False, default=False)
#     num_of_answered_questions = models.PositiveIntegerField(blank=True, null=True)
#     answers_at_end = models.BooleanField(blank=False, default=True)
#     game_trials = models.PositiveIntegerField()
#
#
# class PracticeProgress(models.Model):
#     player = models.ForeignKey(UserManager, on_delete=models.PROTECT)
#     progress = models.CommaSeparatedIntegerField()
#
#
# @python_2_unicode_compatible
# class Question(models.Model):
#     quiz = models.ManyToManyField(Wordbook,
#                                   verbose_name='Quiz',
#                                   blank=True)

