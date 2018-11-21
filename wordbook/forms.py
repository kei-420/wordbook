from django import forms

from wordbook.models.wordbook import Wordbook, Word
from wordbook.models.quiz import Question, Quiz, MultipleQuestions, QuizTakerAnswer

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


# class QuizTakeForm(forms.Form):
#     def __init__(self, data, questions, *args, **kwargs):
#         super(QuizTakeForm, self).__init__(data, *args, **kwargs)
#         self.questions = questions
#         for question in questions:
#             answer = "question_%d" % question.pk
#             choices = []
#             for answer in question.answer_set().all():
#                 choices.append((answer.pk, answer.answer,))
#             ## May need to pass some initial data, etc:
#             answer = forms.ChoiceField(label=question.question, required=True,
#                                       choices=choices, widget=forms.RadioSelect)
#

class QuizTakeForm(forms.ModelForm):
    class Meta:
        model = QuizTakerAnswer
        fields = ('answer',)

    def __init__(self, *args, **kwargs):
        super(QuizTakeForm, self).__init__(*args, **kwargs)
        question = kwargs.pop('question')
        self.fields['answer'] = forms.ModelChoiceField(
            queryset=MultipleQuestions.objects.filter(question_id=question.pk),
            widget=forms.RadioSelect,
        )

