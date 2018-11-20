from django import forms
import numpy as np
import random
from wordbook.models.wordbook import Wordbook, Word
from wordbook.models.practicegame import Question, Quiz, MultipleQuestions

from django.core.exceptions import ObjectDoesNotExist

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


class QuizCreateForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('name', )

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user')
        super(QuizCreateForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'placeholder': 'クイズタイトル'}

    def clean_name(self):
        name = self.cleaned_data['name']
        return name

    def save(self, commit=True):
        name = super(QuizCreateForm, self).save()
        if commit:
            name.save()
            vocab_list = random_select(self._user)
            for v in vocab_list:
                Question.objects.create(quiz=name.pk, game_word=v)


def random_select(request):
    randomly_selected = np.random.choice(Wordbook.objects.filter(user_id=request.user.pk), 10, replace=False)
    vocab_list = []
    for r in randomly_selected:
        vocab = str(r)
        vocab_list.append(vocab)
    return vocab_list
# class QuestionForm(forms.ModelForm):
#     answer = forms.ModelChoiceField(
#         queryset=MultipleChoices.objects.none(),
#         widget=forms.RadioSelect(),
#         required=True,
#         empty_label=None)
#
#     class Meta:
#         model = UserAnswer
#         fields = ('answer',)
#
#     def __init__(self, *args, **kwargs):
#         multiplechoices = kwargs.pop('multiplechoices')
#         super().__init__(*args, **kwargs)
#         self.fields['answer'].queryset = multiplechoices
#
#     def clean_answer(self):
#         answer = self.cleaned_data['answer']
#         return answer

    # def save(self, commit=True):


