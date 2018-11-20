import numpy as np
import re
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, FormView, DetailView, DeleteView

from wordbook.models.practicegame import Quiz, QuizTaker, CompletedQuiz, Question, MultipleQuestions
from wordbook.models.wordbook import Wordbook, Word
from accounts.models import UserManager

from wordbook.forms import QuizCreateForm

from django.core.paginator import Paginator


@method_decorator([login_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'wordbook/practicegame_list.html'

    def get_queryset(self):
        login_user = self.request.user
        # completed_quizzes = login_user.quizzes.values_list('pk', flat=True)
        # get_completed_quizzes = CompletedQuiz.objects.filter(taker_id=login_user.pk).values('quiz_id')
        queryset = Quiz.objects.filter(taker_id=login_user).annotate(num_questions=Count('questions'))
            # .exclude(pk=get_completed_quizzes)
            # .annotate(questions_count=Count('questions'))
            # .filter(questions_count__gt=0)
        return queryset

# @method_decorator([login_required], name='dispatch')
# class QuizListView(ListView):
#     paginate_by = 10
#     template_name = 'wordbook/practicegame_list.html'
#
#     def get(self, request, *args, **kwargs):
#         queryset_list = Quiz.objects.filter(taker_id=request.user.pk)
#         paginator = Paginator(queryset_list, self.paginate_by)
#         page = self.request.GET.get('page')
#         queryset = paginator.get_page(page)
#         context = {
#             'queryset': queryset,
#         }
#         return render(request, 'wordbook/practicegame_list.html', context)


@method_decorator([login_required], name='dispatch')
class CompletedQuizListView(ListView):
    model = CompletedQuiz
    context_object_name = 'completed_quizzes'
    template_name = 'wordbook/taken_quiz_list.html'

    def get_queryset(self):
        # queryset = self.request.user.completed_quizzes \
        #     .select_related('quiz') \
        #     .order_by('quiz__name')
        queryset = CompletedQuiz.objects.filter(taker_id=self.request.user.pk)
        return queryset


@method_decorator([login_required], name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    # form_class = QuizCreateForm
    fields = ('name',)
    template_name = 'wordbook/quiz_add_form.html'

    # def get_form_kwargs(self):
    #     kwargs = super(QuizCreateView, self).get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     return kwargs

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.taker_id = self.request.user.pk
        quiz.save()
        vocab_list = wordids_random_select(quiz.taker_id)
        for v in vocab_list:
            Question.objects.create(quiz_id=quiz.pk, game_word_id=v['pk'])
        words_randomly_selected(quiz.pk)
        messages.success(self.request, "The quiz '%s' was created with success! Go ahead and take the quiz now!" % quiz)
        return redirect('wordbook:game_list')


def wordids_random_select(user_id):
    randomly_selected = np.random.choice(Wordbook.objects.filter(user_id=user_id).values('pk'), 5, replace=False)
    vocab_list = []
    for r in randomly_selected:
        vocab_list.append(r)
    return vocab_list


def words_randomly_selected(get_quiz_id):
    game_wordids = Question.objects.filter(quiz_id=get_quiz_id).values('game_word__word_id', 'pk')
    q_id_list = []
    for q_id in game_wordids:
        random_choices = np.random.choice(Word.objects.exclude(pk=q_id['game_word__word_id']).values('pk'), 3, replace=False)
        q_id_list.append(random_choices)

    list_for_multiple_choices = []
    for n in range(0, 5):
        for l in q_id_list[n]:
            list_for_multiple_choices.append(l['pk'])

    group_by = 3
    list_divided_by_3 = []
    for l in [list_for_multiple_choices[i:i + group_by] for i in range(0, len(list_for_multiple_choices), group_by)]:
        list_divided_by_3.append(l)

    for n in range(0, 5):
        list_divided_by_3[n][0:0] = [game_wordids[n]['game_word__word_id']]

    # practice_game_idで絞り込んだ、Questionの id 取得

    list_for_question_ids = []
    for q in game_wordids:
        list_for_question_ids.append(q['pk'])

    # 作成したquestion_idそれぞれに対応するword_idを明確にする為の辞書（combined_dict）を作成
    combined_dict = dict(zip(list_for_question_ids, list_divided_by_3))

    # combined_dictからMultipleChoicesテーブルへ保存
    for cd in combined_dict:
        for n in range(0, 4):
            MultipleQuestions(question_id=cd, choices_id=combined_dict[cd][n]).save()


@method_decorator([login_required], name='dispatch')
class QuizDeleteView(DeleteView):
    model = Quiz
    success_url = reverse_lazy('wordbook:game_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)





# class PracticeGameAddView(LoginRequiredMixin, CreateView):
#     """
#
#     PracticeGameAddView creates and saves 10 question ids in Question Table and 30 multiplechoices ids corresponding to
#     its 10 question ids in Multiple Choice Table.
#     In addition, PracticeGameAddView creates a practicegame per each request.
#
#     """
#     # model = PracticeGame
#     success_url = reverse_lazy('wordbook:home')
#
#     def get(self, request, *args, **kwargs):
#         return self.post(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         login_user = UserManager.objects.get(username=request.user)
#         pattern = re.compile(r' ()([0-9]{2}):([0-9]{2}):([0-9]{2}).[0-9]{1,6}')
#         to_set_title = datetime.now()
#         eng_date = re.sub(pattern, r'\1-\2-\3-\4', str(to_set_title))
#         split_date = eng_date.split('-')
#         joining_as_jap_date = '{0}年{1}月{2}日 {3}:{4}:{5}'\
#             .format(split_date[0], split_date[1], split_date[2], split_date[3], split_date[4], split_date[5])
#         # count = PracticeGame.objects.filter(user_id=login_user.pk).count() + 1
#         title = "{0}回目の{1}'s単語クイズ｜日時：{2}".format(count, login_user.username, joining_as_jap_date)
#         # example_url = id_generator()
#         to_get_url = re.sub('\s+', '-', title).lower()
#         url = ''.join(letter for letter in to_get_url if letter.isalnum() or letter == '-')
#
#         # PracticeGame(user_id=login_user.pk, title=title, url=url).save()
#
#         # get_practice_game_id = PracticeGame.objects.get(user_id=login_user.pk, title=title)
#         user_word_data = Wordbook.objects.filter(user=login_user.pk)  # ログイン中のユーザーの単語情報（単語帳に登録されている単語全て）の取得
#         user_wordbook_data = user_word_data.values('pk')  # その id 取得
#         wordbook_randomly_selected = np.random.choice(list(user_wordbook_data), 10, replace=False)
#         list_for_wordbook_randomly_selected = []
#         # forループ内では、Questionテーブルにwordbook_randomly_selectedで取得したデータを基にデータ作成
#         for j in wordbook_randomly_selected:
#             is_wordbook_id = j['pk']
#             list_for_wordbook_randomly_selected.append(is_wordbook_id)
#
#             # Question(wordbook_id=is_wordbook_id, practice_game_id=get_practice_game_id.pk).save()
#
#         # game_words = Question.objects.filter(practice_game_id=get_practice_game_id).values('wordbook__word_id')
#
#         list_for_word_ids = []
#         for g in game_words:
#             is_word_id = g['wordbook__word_id']
#             list_for_word_ids.append(is_word_id)
#
#         list_for_random_choices = []
#         for l in list_for_word_ids:
#             choices = Word.objects.exclude(pk=l).')
#             random_choices = np.random.choice(list(choices), 3, replace=False)
#             list_for_random_choices.append(random_choices)
#
#         list_for_multiple_choices = []
#         for n in range(0, 10):
#             for l in list_for_random_choices[n]:
#                 list_for_multiple_choices.append(l['pk'])
#
#         group_by = 3
#         list_divided_by_3 = []
#         for l in [list_for_multiple_choices[i:i + group_by] for i in
#                   range(0, len(list_for_multiple_choices), group_by)]:
#             list_divided_by_3.append(l)
#
#         for n in range(0, 10):
#             list_divided_by_3[n][0:0] = [game_words[n]['wordbook__word_id']]
#
#         # practice_game_idで絞り込んだ、Questionの id 取得
#         question_ids = Question.objects.filter(practice_game_id=get_practice_game_id.pk).values('pk')
#         list_for_question_ids = []
#         for q in question_ids:
#             list_for_question_ids.append(q['pk'])
#
#         # 作成したquestion_idそれぞれに対応するword_idを明確にする為の辞書（combined_dict）を作成
#         combined_dict = dict(zip(list_for_question_ids, list_divided_by_3))
#
#         # combined_dictからMultipleChoicesテーブルへ保存
#         for cd in combined_dict:
#             for n in range(0, 4):
#                 MultipleChoices(question_id=cd, word_id=combined_dict[cd][n]).save()
#
#         return redirect(reverse('wordbook:game_list'))


# class PracticeGameListView(LoginRequiredMixin, ListView):
#     # model = PracticeGame
#     paginate_by = 10
#     template_name = 'wordbook/practicegame_list.html'
#
#     def get(self, request, *args, **kwargs):
#         # queryset_list = PracticeGame.objects.filter(user_id=request.user.pk, complete=False)
#         paginator = Paginator(queryset_list, self.paginate_by)
#         page = self.request.GET.get('page')
#         queryset = paginator.get_page(page)
#         context = {
#             'queryset': queryset,
#         }
#         return render(request, 'wordbook/practicegame_list.html', context)


# class PracticeGameDeleteView(LoginRequiredMixin, DeleteView):
#     # model = PracticeGame
#     success_url = reverse_lazy('wordbook:game_list')
#
#     def get(self, request, *args, **kwargs):
#         return self.post(request, *args, **kwargs)

# class PracticeGameResetView(LoginRequiredMixin, generic.DeleteView):
#     model = PracticeGame
#     success_url = reverse_lazy('wordbook:home')
#
#     # def get(self, request, *args, **kwargs):
#     #     return self.post(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         game_data = PracticeGame.objects.all().filter(user_id=request.user.pk)
#         game_data.delete()


class PracticeGameDetailView(LoginRequiredMixin, DetailView):
    # model = PracticeGame
    slug_field = 'url'

    def get_context_data(self, **kwargs):
        context = super(PracticeGameDetailView, self).get_context_data(**kwargs)
        return context


class PracticeGamePlayView(LoginRequiredMixin, FormView):
    # form_class = QuestionForm
    template_name = 'wordbook/practicegame_play.html'

    def get_form_kwargs(self):
        kwargs = super(PracticeGamePlayView, self).get_form_kwargs()
        # practice_game = get_object_or_404(PracticeGame, url=self.kwargs['practicegame_name'])
        # questions = Question.objects.filter(practice_game_id=practice_game.pk).values('pk')
        # for q in questions:
        #     kwargs['multiplechoices'] = MultipleChoices.objects.filter(question_id=q['pk']).values('word__vocab_meaning')
            # for q2 in queryset:
            #     kwargs['multiplechoices'] = q2['word__vocab_meaning']
            #     return kwargs
        return kwargs

    def play_game(self, request, **kwargs):
        login_user = request.user
        # practice_game = get_object_or_404(PracticeGame, url=self.kwargs['practice_game'])
        # game = Question.objects.filter(practice_game_id=practice_game.pk).values('wordbook__word__vocab')

        # if practice_game.complete is True:
        render(request, 'wordbook/practicegame_list.html')
        # total_questions = game.count()
        # questions = Question.objects.filter(practice_game_id=practice_game.pk).values('wordbook__word__vocab_meaning')

        # form = QuestionForm(questions=questions, data=request.POST)
        # if not form.is_valid():
        #     context = {
        #         'form': form,
        #         'question': kwargs['questions'],
        #         'game_word': game,
        #     }
        #     return render(request, 'wordbook/practicegame_play.html', context)
        # with transaction.atomic():
        # user_answer = form.save(commit=False)
        # user_answer.user = login_user
        # user_answer.save()

        # PracticeGame.completed(self.kwargs)
        redirect(reverse('wordbook:game_list'))
# # def take_quiz(request, pk):
# #     quiz = get_object_or_404(Question, pk=pk)
# #     login_user = request.user
# #
# #     if login_user.filter(pk=pk).exists():
# #             return render(request, 'students/taken_quiz.html')
# #
# #         total_questions = quiz.questions.count()
# #         unanswered_questions = student.get_unanswered_questions(quiz)
# #         total_unanswered_questions = unanswered_questions.count()
# #         progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
# #         question = unanswered_questions.first()
# #
# #         if request.method == 'POST':
# #             form = TakeQuizForm(question=question, data=request.POST)
# #             if form.is_valid():
# #                 with transaction.atomic():
# #                     student_answer = form.save(commit=False)
# #                     student_answer.student = student
# #                     student_answer.save()
# #                     if student.get_unanswered_questions(quiz).exists():
# #                         return redirect('students:take_quiz', pk)
# #                     else:
# #                         correct_answers = student.quiz_answers.filter(answer__question__quiz=quiz,
# #                                                                       answer__is_correct=True).count()
# #                         score = round((correct_answers / total_questions) * 100.0, 2)
# #                         TakenQuiz.objects.create(student=student, quiz=quiz, score=score)
# #                         if score < 50.0:
# #                             messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (
# #                             quiz.name, score))
# #                         else:
# #                             messages.success(request,
# #                                              'Congratulations! You completed the quiz %s with success! You scored %s points.' % (
# #                                              quiz.name, score))
# #                         return redirect('students:quiz_list')
# #         else:
# #             form = TakeQuizForm(question=question)
# #
# #         return render(request, 'classroom/students/take_quiz_form.html', {
# #             'quiz': quiz,
# #             'question': question,
# #             'form': form,
# #             'progress': progress
# #         })
# #
# #         return super(QuizTake, self).dispatch(request, *args, **kwargs)
#
#
#
#     # def get_form_kwargs(self):
#     #     kwargs = super(RepeatedGameView, self).get_form_kwargs()
#     #     kwargs['user'] = self.request.user
#     #     return kwargs
#         # forを抜けた後用に空のリストを用意。
#
#         #     # if not Question.objects.filter(wordbook=i.pk).exists():
#         #     each_user_wordbook_data = Wordbook.objects.get(pk=i.pk)
#         #     create_questions = Question(wordbook=each_user_wordbook_data)
#         #     create_questions.save()
#
#
#
# # def play_game(request, pk):
# #     user_info = UserManager.objects.get(username=request.user)  # ユーザー情報の取得
# #     #  PracticeGameContext(user_id=user_info.pk).save()  # PracticeGameContextテーブルにデータ作成
# #     game = get_object_or_404(PracticeGame, pk=pk)
# #
# #
# #
# #             user_word_data = Wordbook.objects.filter(user=request.user)  # ログイン中のユーザーの単語情報（単語帳に登録されている単語全て）の取得
# #             user_wordbook_data = user_word_data.values('pk')  # その id 取得
# #
# #             # Wordbookからユーザーで絞り込んだid をランダムに１０個取得。
# #             wordbook_randomly_selected = np.random.choice(list(user_wordbook_data), 10, replace=False)
# #
# #             list_for_wordbook_randomly_selected = []
# #             # forループ内では、Questionテーブルにwordbook_randomly_selectedで取得したデータを基にデータ作成
# #             for j in wordbook_randomly_selected:
# #                 is_wordbook_id = j['pk']
# #                 list_for_wordbook_randomly_selected.append(is_wordbook_id)
# #                 Question(wordbook_id=is_wordbook_id, practice_game_id=latest_game_record['pk']).save()
# #
# #             # wordbook_randomly_selectedで選出されたidで絞り込んでword_idの取得。
# #             queryset_of_its_word_ids = []
# #             for l in list_for_wordbook_randomly_selected:
# #                 its_word_ids = Wordbook.objects.filter(pk=l).values('word_id')
# #                 queryset_of_its_word_ids.append(its_word_ids)
# #
# #             list_for_word_ids_queryset = []
# #             for l in queryset_of_its_word_ids:
# #                 for entry in l:
# #                     is_word_id = entry['word_id']
# #                     list_for_word_ids_queryset.append(is_word_id)
# #
# #             list_for_random_choices = []
# #             for l in list_for_word_ids_queryset:
# #                 choices = Word.objects.exclude(pk=l).values('pk')
# #                 random_choices = np.random.choice(list(choices), 3, replace=False)
# #                 list_for_random_choices.append(random_choices)
# #
# #             list_for_multiple_choices = []
# #             for n in range(0, 10):
# #                 for l in list_for_random_choices[n]:
# #                     list_for_multiple_choices.append(l['pk'])
# #
# #             group_by = 3
# #             list_divided_by_3 = []
# #             for l in [list_for_multiple_choices[i:i + group_by] for i in
# #                       range(0, len(list_for_multiple_choices), group_by)]:
# #                 list_divided_by_3.append(l)
# #
# #             # practice_game_idで絞り込んだ、Questionの id 取得
# #             question_ids = Question.objects.filter(
# #                 practice_game_id=latest_game_record['pk']).values('pk')
# #
# #             list_for_question_ids = []
# #             for q in question_ids:
# #                 list_for_question_ids.append(q['pk'])
# #
# #             # 作成したquestion_idそれぞれに対応するword_idを明確にする為の辞書（combined_dict）を作成
# #             combined_dict = dict(zip(list_for_question_ids, list_divided_by_3))
# #
# #             # combined_dictからMultipleChoicesテーブルへ保存
# #             for cd in combined_dict:
# #                 for n in range(0, 3):
# #                     MultipleChoices(question_id=cd, word_id=combined_dict[cd][n]).save()
# #
# #             # 保存した選択問題の取得
# #             list_for_get_shown_multiple_choices_data = []
# #             for l in list_for_question_ids:
# #                 get_shown_multiple_choices_data = MultipleChoices.objects.filter(question_id=l).values('word_id')
# #                 list_for_get_shown_multiple_choices_data.append(get_shown_multiple_choices_data)
# #
# #             list_for_after_loop = []
# #             for n in range(0, len(list_for_get_shown_multiple_choices_data)):
# #                 for m in range(0, 3):
# #                     list_for_after_loop.append(list_for_get_shown_multiple_choices_data[n][m]['word_id'])
# #
# #             list_for_its_loop = []
# #             for n in range(0, len(list_for_after_loop)):
# #                 list_for_its_loop.append(list_for_after_loop[n])
# #
# #             group_by = 3
# #             list_divided_by_3_shown = []
# #             for l in [list_for_its_loop[i:i + group_by] for i in
# #                       range(0, len(list_for_its_loop), group_by)]:
# #                 list_divided_by_3_shown.append(l)
# #
# #             list_for_exec_query2 = []
# #             for l in list_for_question_ids:
# #                 list_for_exec_query2.append(MultipleChoices.exec_query2(l))
# #
# #             list_for_slicing = []
# #             for l in list_for_exec_query2:
# #                 list_for_slicing.append(l[0]['word_id'])
# #
# #             list_for_zip = []
# #             for l1, l2 in zip(list_divided_by_3_shown, list_for_slicing):
# #                 list_for_zip.append(l1 + [l2])
# #
# #             list_for_vocab_meanings = []
# #             for n in range(0, len(list_for_zip)):
# #                 for l in list_for_zip[n]:
# #                     get_vocab_meanings = Word.objects.filter(pk=l).values('vocab_meaning')
# #                     list_for_vocab_meanings.append(get_vocab_meanings)
# #
# #             group_by2 = 4
# #             shown_list = []
# #             for l in [list_for_vocab_meanings[i:i + group_by2] for i in
# #                       range(0, len(list_for_vocab_meanings), group_by2)]:
# #                 shown_list.append(l)
# #
# #             context = {
# #                 'shown_list': shown_list,
# #             }
# #             render(request, 'wordbook/repeated_game.html', context)
# #
