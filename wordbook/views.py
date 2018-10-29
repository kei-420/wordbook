from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View, generic
import numpy as np
import random

from django.urls import reverse_lazy

from .forms import WordAddForm

from .models import Word, Wordbook, RepeatedGame


class HomeView(LoginRequiredMixin, generic.ListView):
    paginate_by = 10
    template_name = 'wordbook/home.html'

    def get(self, request, *args, **kwargs):
        show_data = Word.objects.filter(wordbook__user=request.user).order_by('vocab')
        context = {
            'show_data': show_data,
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

        return redirect(reverse('wordbook:home'))


class RepeatedGameView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        global is_game_word, is_answer, are_elements
        user_word_data = Wordbook.objects.filter(user=request.user)
        is_randomly_selected = np.random.choice(
            list(user_word_data.values('word__vocab', 'word__vocab_meaning')),
            5,
            replace=False,
        )
        for j in is_randomly_selected:
            is_game_word = j["word__vocab"]
            is_answer = j["word__vocab_meaning"]

        choices = Word.objects.exclude(vocab_meaning=is_answer).values('vocab_meaning')
        random_choices = np.random.choice(list(choices), 3, replace=False)
        list_random_choices = []
        for n in range(0, 3):
            are_elements = random_choices[n]["vocab_meaning"]
            list_random_choices.append(are_elements)
        list_random_choices.append(is_answer)
        random.shuffle(list_random_choices)
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
