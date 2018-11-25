from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.views.generic import ListView, FormView, DeleteView
from django.urls import reverse_lazy

from wordbook.forms import WordAddForm
from wordbook.models.wordbook import Wordbook

from django.core.paginator import Paginator

from django.contrib import messages

from bootstrap_modal_forms.mixins import PassRequestMixin


@method_decorator([login_required], name='dispatch')
class HomeView(ListView):
    model = Wordbook
    paginate_by = 12
    template_name = 'wordbook/home.html'

    def get(self, request, *args, **kwargs):
        queryset_list = Wordbook.exec_query(request.user.pk)
        paginator = Paginator(queryset_list, self.paginate_by)

        page = self.request.GET.get('page')

        queryset = paginator.get_page(page)
        context = {
            'queryset': queryset,
        }
        return render(request, 'wordbook/home.html', context)


@method_decorator([login_required], name='dispatch')
class WordAddView(FormView):
    form_class = WordAddForm
    template_name = 'wordbook/word_add.html'
    success_url = reverse_lazy('wordbook:home')

    def get_form_kwargs(self):
        kwargs = super(WordAddView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        form = WordAddForm(request.POST, user=request.user)
        if not form.is_valid():
            return render(request, 'wordbook/word_add.html', {'form': form})
        form.save(commit=True)
        messages.success(request, "'%s' has been just added" % form.cleaned_data['adding_word'])
        return redirect('wordbook:home')


@method_decorator([login_required], name='dispatch')
class WordDeleteView(DeleteView):
    model = Wordbook
    success_url = reverse_lazy('wordbook:home')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)