import numpy as np
import random

from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views import View, generic
from django.urls import reverse_lazy

from .forms import WordAddForm
from .models import Wordbook, Word

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


class HomeView(LoginRequiredMixin, generic.ListView):
    model = Wordbook
    paginate_by = 12
    template_name = 'wordbook/home.html'

    def get(self, request, *args, **kwargs):
        queryset_list = Wordbook.exec_query(request.user.pk)
        paginator = Paginator(queryset_list, self.paginate_by)

        page = self.request.GET.get('page')

        # try:
        # queryset = paginator.page(page)
        queryset = paginator.get_page(page)
        # except PageNotAnInteger:
        #     queryset = paginator.page(1)
        # except EmptyPage:
        #     queryset = paginator.page(paginator.num_pages)
        # show_list = Wordbook.exec_query(request.user.pk)
        # show_list = Word.objects.filter(wordbook__user_id=request.user)

        # a = Wordbook.objects.filter(word__wordbook__user_id=request.user)
        context = {
            # 'show_list': show_list,
            'queryset': queryset,
        }
        return render(request, 'wordbook/home.html', context)


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


class WordDeleteView(generic.DeleteView):
    model = Wordbook
    success_url = reverse_lazy('wordbook:home')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class RepeatedGameView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        global is_game_word, is_answer
        # 現在ログイン中のユーザー情報から単語データを取得。
        user_word_data = Wordbook.objects.filter(user=request.user)
        # リストからランダム抽出（"word__vocab"と"word_meaning__vocab_meaning"）＆重複なし。
        is_randomly_selected = np.random.choice(
            list(user_word_data.values('word__vocab', 'word__vocab_meaning')),
            1,
            replace=False,
        )
        # for内では特定の要素の取得
        for j in is_randomly_selected:
            # 出題される単語
            is_game_word = j['word__vocab']
            # 答えである意味
            is_answer = j['word__vocab_meaning']

        # ４つの選択肢のうち、答え以外の３つの取得かつ、その３つが答えと重複しないようにした。
        choices = Word.objects.exclude(vocab_meaning=is_answer).values('vocab_meaning')
        # リストからランダム抽出。重複なし。
        random_choices = np.random.choice(list(choices), 3, replace=False)
        # forを抜けた後用に空のリストを用意。
        list_random_choices = []
        # for内では残り３つの選択肢の取得。
        for n in range(0, 3):
            are_elements = random_choices[n]['vocab_meaning']
            # 取得したデータを空リスト内に格納。
            list_random_choices.append(are_elements)
        # 加えて、答えもその中に格納
        list_random_choices.append(is_answer)
        # ランダムに選択肢を表示する為にシャッフル。
        random.shuffle(list_random_choices)
        # choice1 ~ choice4までの定義
        choice1 = list_random_choices[0]
        choice2 = list_random_choices[1]
        choice3 = list_random_choices[2]
        choice4 = list_random_choices[3]

        context = {
            'is_game_word': is_game_word,
            'choice1': choice1,
            'choice2': choice2,
            'choice3': choice3,
            'choice4': choice4,
        }
        return render(request, 'wordbook/repeated_game.html', context)

    # def post(self, request, *args, **kwargs):

