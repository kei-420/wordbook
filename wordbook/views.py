from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View, generic

from .forms import WordAddForm

from .models import Word


class HomeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        word_data = Word.objects.filter(wordbook__user=request.user).order_by('vocab')
        context = {
            'show_data': word_data,
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
