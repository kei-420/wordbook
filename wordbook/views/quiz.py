import numpy as np
import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, DeleteView, DetailView

from wordbook.models.quiz import Quiz, CompletedQuiz, Question, MultipleQuestions, QuizTakerAnswer, QuizLength
from wordbook.models.wordbook import Wordbook, Word
from wordbook.forms import QuizTakeForm


@method_decorator([login_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'wordbook/quiz_list.html'

    def get_queryset(self):
        login_user = self.request.user.quiztaker
        get_completed_quizzes = login_user.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.exclude(pk__in=get_completed_quizzes).annotate(num_questions=Count('questions'))
        return queryset


@method_decorator([login_required], name='dispatch')
class CompletedQuizListView(ListView):
    model = CompletedQuiz
    context_object_name = 'completed_quizzes'
    template_name = 'wordbook/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.quiztaker.completed_quizzes.select_related('quiz')
        return queryset


@method_decorator([login_required], name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    fields = ('name', 'length')
    template_name = 'wordbook/quiz_add_form.html'

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.taker_id = self.request.user.pk
        quiz.save()
        quiz_length = get_object_or_404(QuizLength, pk=quiz.length_id)
        if Wordbook.objects.filter(user_id=self.request.user.pk).count() < quiz_length.length:
            messages.error(
                self.request,
                "Your wordbook owns less than %s words. Add more to create a quiz." % str(quiz_length.length)
            )

        vocab_list = wordids_random_select(quiz.taker_id, quiz_length.length)
        for v in vocab_list:
            Question.objects.create(quiz_id=quiz.pk, game_word_id=v['word_id'])
        words_randomly_selected(quiz.pk, quiz_length.length)
        game_word_ids = Question.objects.filter(quiz_id=quiz.pk).values('game_word', 'pk')
        for gwi in game_word_ids:
            if MultipleQuestions.objects.filter(question=gwi['pk']).exists():
                get_vocab_meaning = get_object_or_404(Word, pk=gwi['game_word'])
                turn_to_true = MultipleQuestions.objects.filter(meaning=get_vocab_meaning.vocab_meaning).filter(question=gwi['pk']).first()
                turn_to_true.is_correct = True
                turn_to_true.save()

        messages.success(self.request, "The quiz '%s' was created with success! Go ahead and take the quiz now!" % quiz)
        return redirect('wordbook:quiz_list')


def wordids_random_select(user_id, quiz_length):
    randomly_selected = np.random.choice(list(Wordbook.objects.filter(user_id=user_id).values('word_id')), quiz_length, replace=False)
    vocab_list = []
    for r in randomly_selected:
        vocab_list.append(r)
    return vocab_list


def words_randomly_selected(get_quiz_id, quiz_length):
    game_wordids = Question.objects.filter(quiz_id=get_quiz_id).values('game_word', 'pk')
    q_id_list = []
    for q_id in game_wordids:
        random_choices = np.random.choice(Word.objects.exclude(pk=q_id['game_word']).values('pk'), 3, replace=False)
        q_id_list.append(random_choices)

    list_for_multiple_choices = []
    for n in range(0, quiz_length):
        for l in q_id_list[n]:
            list_for_multiple_choices.append(l['pk'])

    group_by = 3
    list_divided_by_3 = []
    for l in [list_for_multiple_choices[i:i + group_by] for i in range(0, len(list_for_multiple_choices), group_by)]:
        list_divided_by_3.append(l)

    for n in range(0, quiz_length):
        list_divided_by_3[n][0:0] = [game_wordids[n]['game_word']]

    for ldb3 in list_divided_by_3:
        random.shuffle(ldb3)

    # practice_game_idで絞り込んだ、Questionの id 取得
    list_for_question_ids = []
    for q in game_wordids:
        list_for_question_ids.append(q['pk'])

    # 作成したquestion_idそれぞれに対応するword_idを明確にする為の辞書（combined_dict）を作成
    combined_dict = dict(zip(list_for_question_ids, list_divided_by_3))
    # combined_dictからMultipleChoicesテーブルへ保存
    for cd in combined_dict:
        for n in range(0, 4):
            vocab = get_object_or_404(Word, pk=combined_dict[cd][n])
            MultipleQuestions(meaning=vocab.vocab_meaning, question_id=cd).save()


@method_decorator([login_required], name='dispatch')
class QuizDeleteView(DeleteView):
    model = Quiz
    success_url = reverse_lazy('wordbook:quiz_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


@login_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    login_user = request.user.quiztaker

    if login_user.quizzes.filter(pk=pk).exists():
        return render(request, 'wordbook/taken_quiz_list.html')

    total_questions = quiz.questions.count()
    unanswered_questions = login_user.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()
    # question_list = quiz.questions.values_list('answers__choices__vocab_meaning', flat=True)

    if request.method == 'POST':
        quiz_form = QuizTakeForm(question=question, data=request.POST)
        # question_form = QuizShowForm(data=request.POST)
        if quiz_form.is_valid():
            with transaction.atomic():
                user_answer = quiz_form.save(commit=False)
                # user_answer.is_user_answer = True
                # quiz_taker = QuizTakerAnswer()
                # quiz_taker.taker = login_user
                # quiz_taker.answer = user_answer
                # quiz_taker.save()
                user_answer.taker = login_user
                user_answer.save()
                if login_user.get_unanswered_questions(quiz).exists():
                    return redirect('wordbook:quiz_take', pk)
                else:
                    correct_answers = login_user.quiz_answers.filter(
                        answer__question__quiz=quiz,
                        answer__is_correct=True,
                    ).count()
                    score = round((correct_answers / total_questions) * 100.0, 2)
                    CompletedQuiz.objects.create(user=login_user, quiz=quiz, score=score)
                    if score < 50.0:
                        messages.error(
                            request,
                            'Do better next time! Your score for the quiz %s was %s/100'
                            % (quiz, score),
                        )
                    elif 50 <= score < 80:
                        messages.warning(
                            request,
                            'Better luck next time! Your score for the quiz %s was %s/100.'
                            % (quiz, score),
                        )
                    else:
                        messages.success(
                            request,
                            'Great Job! You completed the quiz %s with a high score, %s/100.'
                            % (quiz, score),
                        )
                    return redirect('wordbook:quiz_list')
    else:
        quiz_form = QuizTakeForm(question=question)
        # question_form = QuizShowForm()

    return render(request, 'wordbook/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'quiz_form': quiz_form,
        'progress': progress,

    })


@method_decorator([login_required], name='dispatch')
class CompletedQuizDetailView(DetailView):
    model = CompletedQuiz

    def get_queryset(self):
        login_user = self.request.user.quiztaker
        queryset = login_user.quiz_answers.filter(pk=login_user)
        return queryset


@method_decorator([login_required], name='dispatch')
class CompletedQuizDeleteView(DeleteView):
    model = CompletedQuiz
    success_url = reverse_lazy('wordbook:completed_quiz_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

# @method_decorator([login_required], name='dispatch')
# class DetailedCompletedQuizView(DetailView):
