from django import forms
from .models import Wordbook, Word, WordMeanings


# def search_word_meanings(word):
#     wordid = Word.objects.filter(vocab=word).values('wordid')
#     wordid_list = []
#     for row in wordid:
#         word = row['wordid']
#         wordid_list.append(word)
#
#     word_meanings_list = []
#     for row1 in wordid_list:
#         get_word_meanings = WordMeanings.objects.filter(wordid=row1, lang='jpn').values('vocab_meaning')
#         for row2 in get_word_meanings:
#             get_its_meanings = row2['vocab_meaning']
#             word_meanings_list.append(get_its_meanings)
#
#     return word_meanings_list


class WordAddForm(forms.ModelForm):
    class Meta:
        model = Wordbook
        fields = ('adding_word', )

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user')
        super(WordAddForm, self).__init__(*args, **kwargs)
        self.fields['adding_word'].widget.attrs = {'placeholder': '追加単語'}

    def clean_adding_word(self):
        adding_word = self.cleaned_data['adding_word']
        if not Word.objects.filter(vocab=adding_word):
            raise forms.ValidationError('入力された単語は存在しません。\n'
                                        'スペル等を確認して下さい。')
        if Wordbook.objects.filter(adding_word=adding_word, user_id=self._user).exists():
            raise forms.ValidationError('入力された単語は既に単語帳内に存在しています。')
        return adding_word

    def save(self, commit=True):
        word_info = super(WordAddForm, self).save(commit=False)
        get_word_id = Word.objects.filter(vocab=word_info).first()
        get_word_meaning_id = WordMeanings.objects.filter(wordid=get_word_id.wordid, lang='jpn').values('pk').first()
        word_info.word_id = get_word_id.pk
        word_info.word_meaning_id = get_word_meaning_id['pk']
        word_info.user = self._user
        if commit:
            word_info.save()
        return word_info



        #
        # get_word_id = Word.objects.filter(vocab=word_info).values('wordid')
        # get_word_meanings = WordMeanings.objects.filter(wordid=get_word_id).get()
        # word_info.word_id = get_word_meanings.pk
        # word_info.user = self._user
        #
        # if commit:
        #     word_info.save()
        # return word_info


# CHOICES = {
#     ('0', 'a'),
#     ('1', 'b'),
#     ('2', 'c'),
#     ('3', 'd'),
# }
#
#
# class RepeatedGameForm(forms.Form):
#     user_choices = forms.ChoiceField(label='属性', widget=forms.RadioSelect, choices=CHOICES)
#
#     def __init__(self, *args, **kwargs):
#         self.user = kwargs.pop('user', None)
#         super(RepeatedGameForm, self).__init__(*args, **kwargs)
#
#     def clean_user_choices(self):
#         user_choices = self.cleaned_data['user_choices']
#         return user_choices

# class RepeatedGameForm(forms.Form):
#     answers = forms.ChoiceField(widget=forms.RadioSelect(), label=u"Please select a answer:")
#
#     def __init__(self, question, *args, **kwargs):
#         super(RepeatedGameForm, self).__init__(*args, **kwargs)
#         self.question = question
#         answers = question.answers.order_by('weight')
#         self.fields['answers'].choices = [(i, a.answer) for i, a in enumerate(answers)]
#
#         for pos, answer in enumerate(answers):
#             if answer.id == question.correct_answer_id:
#                 self.correct = pos
#             break
#
#     def is_correct(self):
#         if not self.is_valid():
#             return False
#
#         return self.cleaned_data['answers'] == str(self.question.correct_answer.id)


# def quiz_forms(user, data=None):
#     questions = Wordbook.objects.filter(user=user)
#     form_list = []
#     for pos, question in enumerate(questions):
#         form_list.append(RepeatedGameForm(question, data, prefix=pos))
#     return form_list


# class QuizForm(forms.Form):
#     choices = forms.ModelChoiceField(queryset=MultipleChoiceAnswer.objects.none(),widget=forms.CheckboxSelectMultiple, required=True, show_hidden_initial=True)
#
#     def __init__(self, question):
#         super(QuizForm, self).__init__()
#         self.fields['choices'].queryset = question.choices.all()
#         self.fields['choices'].empty_label = None
#
#
# class QuizForm2(forms.Form):
#     def __init__(self, question, *args, **kwargs):
#         super(QuizForm2, self).__init__(*args, **kwargs)
#         self.fields['choices'] = forms.ChoiceField(widget=forms.CheckboxSelectMultiple, choices=[ (x.id, x.answer) for x in question.choices.all()])
