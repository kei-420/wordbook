from django.shortcuts import render, redirect, reverse, HttpResponseRedirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View, generic
import numpy as np
import random
from django.db import connection

from django.urls import reverse_lazy

from .forms import WordAddForm

from .models import Word, Wordbook, WordMeanings


# def search_word_meanings(word):
#     wordid = Word.objects.filter(vocab=word).values('wordid')
#     wordid_list = []
#     for row in wordid:
#         get_its_words = row['wordid']
#         wordid_list.append(get_its_words)
#
#     word_meanings_list = []
#     for row1 in wordid_list:
#         get_word_meanings = WordMeanings.objects.filter(wordid=row1, lang='jpn').values('vocab_meaning')
#         for row2 in get_word_meanings:
#             get_its_meanings = row2['vocab_meaning']
#             word_meanings_list.append(get_its_meanings)
#
#     return word_meanings_list[0]


def exec_query(sqltext):
    with connection.cursor() as cur:
        cur.execute(sqltext)
        columns = [col[0] for col in cur.description]
        dict1 = [dict(zip(columns, row)) for row in cur.fetchall()]
        return dict1


class HomeView(LoginRequiredMixin, generic.ListView):
    paginate_by = 10
    template_name = 'wordbook/home.html'

    def get(self, request, *args, **kwargs):
        global words_list
        words = Word.objects.filter(wordbook__user=request.user).values('vocab')
        sqltext_list = []
        for w in words:
            sqltext = """
            SELECT vocab, vocab_class, vocab_meaning FROM word
            INNER JOIN word_meanings
            ON word.wordid = word_meanings.wordid
            WHERE word.vocab='%s' and word_meanings.lang='jpn'
            """ % w['vocab']
            sqltext_list.append(sqltext)
            for s in sqltext_list:
                words_list = exec_query(s)
                return render(request, 'wordbook/home.html', {'show_word': words_list})

        # get_word_and_its_class = Word.objects.filter(wordbook__user=1).order_by('vocab')
        # get_words = get_word_and_its_class.values('vocab')
        # words_list = []
        # for entry in get_words:
        #     each_word = entry['vocab']
        #     words_list.append(each_word)

        # get_wordids = get_word_and_its_class.values('wordid')
        # # meanings_list = []
        # for entry in get_wordids:
        #     get_meanings = WordMeanings.objects.filter(wordid=entry['wordid'], lang='jpn').values('vocab_meaning')
        #     # for entry2 in get_meanings:
        #     #     each_meaning = entry2['vocab_meaning']
        #     #  meanings_list.append(each_meaning)
        # # dictionary = dict(zip(words_list, meanings_list))
        #     context = {
        #         'show_word': get_word_and_its_class,
        #         'show_meaning': get_meanings,
        #     }

class WordAddView(LoginRequiredMixin, generic.FormView):
    form_class = WordAddForm
    template_name = 'wordbook/word_add.html'

    def get_form_kwargs(self):
        kwargs = super(WordAddView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        form = WordAddForm(request.POST, user=request.user)
        if not form.is_valid():
            return render(request, 'wordbook/word_add.html', {'form': form})
        form.save(commit=True)

        return redirect('wordbook:home')
#
# class WordAddView(LoginRequiredMixin, generic.FormView):
#     form_class = WordAddForm
#     template_name = 'wordbook/word_add.html'
#
#     def get_form_kwargs(self):
#         kwargs = super(WordAddView, self).get_form_kwargs()
#         kwargs['user'] = self.request.user
#         return kwargs
#
#     def post(self, request, *args, **kwargs):
#         form = WordAddForm(request.POST, user=request.user)
#         if not form.is_valid():
#             return render(request, 'wordbook/word_add.html', {'form': form})
#
#         form.save(commit=True)
#
#         return redirect(reverse('wordbook:home'))
#
#
# # def word_delete(pk=None):
# #     instance = Wordbook.objects.filter(pk=pk)
# #     instance.delete()
# #     return redirect(reverse("wordbook:home"))
#


class WordDeleteView(generic.DeleteView):
    model = Wordbook
    success_url = reverse_lazy('wordbook:home')
# #
# #
#
#
# class RepeatedGameView(LoginRequiredMixin, View):
#     def get(self, request, *args, **kwargs):
#         global is_game_word, is_answer
#         # form = RepeatedGameForm
#         # form = RepeatedGameForm()
#         # 現在ログイン中のユーザー情報から単語データを取得。
#         user_word_data = Wordbook.objects.filter(user=request.user)
#         # リストからランダム抽出（"word__vocab"と"word__vocab_meaning"）＆重複なし。
#         is_randomly_selected = np.random.choice(
#             list(user_word_data.values('word__vocab', 'word__vocab_meaning')),
#             1,
#             replace=False,
#         )
#         # for内では特定の要素の取得
#         for j in is_randomly_selected:
#             # 出題される単語
#             is_game_word = j['word__vocab']
#             # 答えである意味
#             is_answer = j['word__vocab_meaning']
#
#         # ４つの選択肢のうち、答え以外の３つの取得かつ、その３つが答えと重複しないようにした。
#         choices = Word.objects.exclude(vocab_meaning=is_answer).values('vocab_meaning')
#         # リストからランダム抽出。重複なし。
#         random_choices = np.random.choice(list(choices), 3, replace=False)
#         # forを抜けた後用に空のリストを用意。
#         list_random_choices = []
#         # for内では残り３つの選択肢の取得。
#         for n in range(0, 3):
#             are_elements = random_choices[n]['vocab_meaning']
#             # 取得したデータを空リスト内に格納。
#             list_random_choices.append(are_elements)
#         # 加えて、答えもその中に格納
#         list_random_choices.append(is_answer)
#         # ランダムに選択肢を表示する為にシャッフル。
#         random.shuffle(list_random_choices)
#         # choice1 ~ choice4までの定義
#         choice1 = list_random_choices[0]
#         choice2 = list_random_choices[1]
#         choice3 = list_random_choices[2]
#         choice4 = list_random_choices[3]
#
#         context = {
#             'is_game_word': is_game_word,
#             'choice1': choice1,
#             'choice2': choice2,
#             'choice3': choice3,
#             'choice4': choice4,
#             # 'form': form,
#         }
#         return render(request, 'wordbook/repeated_game.html', context)
#     #
#     # def post(self, request, *args, **kwargs):
#     #     if request.method == 'POST':
#     #         for wo