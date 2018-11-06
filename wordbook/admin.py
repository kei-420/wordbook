from django.contrib import admin
from .models import Wordbook, Word, WordMeanings
#
# admin.site.register(Word)
# admin.site.register(Wordbook)
# admin.site.register(RepeatedGame)

admin.site.register(Word)
admin.site.register(Wordbook)
admin.site.register(WordMeanings)
