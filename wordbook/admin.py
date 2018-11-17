from django.contrib import admin
from .models import Wordbook, Word, PracticeGame
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



