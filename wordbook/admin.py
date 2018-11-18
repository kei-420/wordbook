from django.contrib import admin
from wordbook.models.wordbook import Wordbook, Word
from wordbook.models.practicegame import PracticeGame
# admin.site.register(Word)
# admin.site.register(Wordbook)
# admin.site.register(RepeatedGame)


# class PracticeGameAdmin(admin.ModelAdmin):
#     form = PracticeGameAdminForm
#
#     list_display = ('title', )


admin.site.register(Word)
admin.site.register(Wordbook)
admin.site.register(PracticeGame)



