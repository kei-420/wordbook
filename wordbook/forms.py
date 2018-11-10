from django import forms
from .models import Wordbook, Word


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
        reverse_search_word = Word.objects.filter(vocab_meaning__contains=adding_word)
        if reverse_search_word.exists():
            for entry in reverse_search_word:
                adding_word = entry
        else:
            raise forms.ValidationError('入力された日本語に該当する英単語は存在しません。')
        if not Word.objects.filter(vocab=adding_word):
            raise forms.ValidationError('入力された単語は存在しません。\n'
                                        'スペル等を確認して下さい。')
        if Wordbook.objects.filter(adding_word=adding_word, user_id=self._user).exists():
            raise forms.ValidationError('入力された単語は既に単語帳内に存在しています。')
        return adding_word

    def save(self, commit=True):
        word_info = super(WordAddForm, self).save(commit=False)
        get_word_id = list(Word.objects.filter(vocab=word_info).values('pk'))
        # get_word_id2 = list(Word.objects.filter(vocab_meaning__contains=word_info).values('pk'))
        # get_word_meaning_id = WordMeanings.objects.filter(wordid=get_word_id.wordid, lang='jpn').values('pk').first()
        word_info.word_id = get_word_id[0]['pk']
        # word_info.word_meaning_id = get_word_meaning_id['pk']
        word_info.user = self._user
        if commit:
            word_info.save()
        return word_info
