from django.contrib import admin
from .models import Wordbook, Word, RepeatedGame


admin.site.register(Word)
admin.site.register(Wordbook)
admin.site.register(RepeatedGame)