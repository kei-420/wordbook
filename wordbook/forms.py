from django import forms

from wordbook.models.wordbook import Wordbook, Word
from wordbook.models.quiz import MultipleQuestions, QuizTakerAnswer


class WordAddForm(forms.ModelForm):
    class Meta:
        model = Wordbook
        fields = ('adding_word', )

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user')
        super(WordAddForm, self).__init__(*args, **kwargs)
        self.fields['adding_word'].widget.attrs = {'placeholder': '追加単語'}
        self.fields['adding_word'].auto_focus = True

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


# class QuizCreateForm(forms.ModelForm):
#
#     class Meta:
#         model = Quiz
#         fields = ('name', 'length', )
#
#     def __init__(self, *args, **kwargs):
#         super(QuizCreateForm, self).__init__(*args, **kwargs)
#         self.fields['name'].widget.attrs = {'placeholder': 'タイトル'}
#         self.fields['length'] = forms.ChoiceField(choices={5, 10, 15}, widget=forms.Select(), label='問題数を選んでください。')


class QuizTakeForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=MultipleQuestions.objects.none(),
        widget=forms.RadioSelect,
        required=True,
        empty_label=None,
    )

    class Meta:
        model = QuizTakerAnswer
        fields = ('answer', )

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super(QuizTakeForm, self).__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.order_by('meaning')




