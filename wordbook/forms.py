from django import forms
from .models import Wordbook, Word, PracticeGameContext, Question, MultipleChoices, PracticeGame
from django.forms.widgets import RadioSelect, Textarea
from django.contrib.admin.widgets import FilteredSelectMultiple


class WordAddForm(forms.ModelForm):
    class Meta:
        model = Wordbook
        fields = ('adding_word', )

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user')
        super(WordAddForm, self).__init__(*args, **kwargs)
        self.fields['adding_word'].widget.attrs = {'placeholder': '追加単語'}

    def clean_adding_word(self):
        adding_word = self.cleaned_data['adding_word'].lower()
        if not Word.objects.filter(vocab=adding_word):
            raise forms.ValidationError('入力された単語は存在しません。\n'
                                        'スペル等を確認して下さい。')
        if Wordbook.objects.filter(adding_word=adding_word, user_id=self._user).exists():
            raise forms.ValidationError('入力された単語は既に単語帳内に存在しています。')
        return adding_word

    def save(self, commit=True):
        word_info = super(WordAddForm, self).save(commit=False)
        get_word_id = list(Word.objects.filter(vocab=word_info).values('pk'))
        word_info.word_id = get_word_id[0]['pk']
        word_info.user = self._user
        if commit:
            word_info.save()
        return word_info


# class PracticeGameAddForm(forms.ModelForm):
#     class Meta:
#         model = PracticeGame
#         fields = ('title',)
#
#     def __init__(self, *args, **kwargs):
#         super(PracticeGameAddForm, self).__init__(*args, **kwargs)
#         self.fields['title'].widget.attrs = {'placeholder': 'タイトル'}
#
#     def clean_title(self):
#         title = self.cleaned_data['title']
#         return title

# class PracticeGameAdminForm(forms.ModelForm):
#     """
#     below is from
#     http://stackoverflow.com/questions/11657682/
#     django-admin-interface-using-horizontal-filter-with-
#     inline-manytomany-field
#     """
#
#     class Meta:
#         model = PracticeGame
#         exclude = []
#
#     questions = forms.ModelMultipleChoiceField(
#         queryset=Question.objects.all(),
#         required=False,
#         label='Questions',
#         widget=FilteredSelectMultiple(
#             verbose_name='Questions',
#             is_stacked=False,
#         )
#     )
#
#     def __init__(self, *args, **kwargs):
#         super(PracticeGameAdminForm, self).__init__(*args, **kwargs)
#         if self.instance.pk:
#             self.fields['questions'].initial =\
#                 self.instance.question_set.all().select_subclasses()
#
#     def save(self, commit=True):
#         game = super(PracticeGameAdminForm, self).save(commit=False)
#         game.question_set = self.cleaned_data['questions']
#         self.save_m2m()
#         return game


class QuestionForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        choice_list = [x for x in question.get_answers_list()]
        self.fields["answers"] = forms.ChoiceField(choices=choice_list,
                                                   widget=RadioSelect)


# TEST_CHOICES = [
#     {'1': MultipleChoices.objects.filter(question_id=)},
#     {'2': MultipleChoices.objects.filter(question_id=)},
#     {'3': MultipleChoices.objects.filter(question_id=)},
#     {'4': MultipleChoices.objects.filter(question_id=)},
# ]


# class PracticeGameForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         self._user = kwargs.pop('multiple_choices')
#         super(PracticeGameForm, self).__init__(*args, **kwargs)
#
#     TEST_CHOICES = {
#         '1': MultipleChoices.objects.filter(question_id=)
#     }
#     test = forms.MultipleChoiceField(
#         choices=TEST_CHOICES,
#         widget=forms.CheckboxSelectMultiple(),
#         required=False,
#     )
#
#     # def __init__(self, *args, **kwargs):
#     #     super(PracticeGameForm, self).__init__(*args, **kwargs)
#     #     self._user = kwargs.pop('user')
#
#     def clean_test(self):
#         test = self.cleaned_data['test']
#         return test

