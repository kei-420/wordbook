import numpy as np
import re
from datetime import datetime

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from django.views import generic
from django.urls import reverse_lazy

from wordbook.forms import WordAddForm, QuestionForm
from wordbook.models.wordbook import Wordbook, Word
from wordbook.models.practicegame import PracticeGame, Question, MultipleChoices, UserProgress, UserAnswer
from accounts.models import UserManager


class PracticeGameAddView(LoginRequiredMixin, generic.CreateView):
    model = PracticeGame
    success_url = reverse_lazy('wordbook:home')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user_info = UserManager.objects.get(username=request.user)
        pattern = re.compile(r' ()([0-9]{2}):([0-9]{2}):([0-9]{2}).[0-9]{1,6}')
        to_set_title = datetime.now()
        eng_date = re.sub(pattern, r'\1-\2-\3-\4', str(to_set_title))
        split_date = eng_date.split('-')
        joining_as_jap_date = '{0}年{1}月{2}日 {3}:{4}:{5}'\
            .format(split_date[0], split_date[1], split_date[2], split_date[3], split_date[4], split_date[5])
        count = PracticeGame.objects.filter(user_id=user_info.pk).count() + 1
        title = "{0}回目の{1}'s単語クイズ｜{2}".format(count, user_info.username, joining_as_jap_date)
        # example_url = id_generator()
        to_get_url = re.sub('\s+', '-', title).lower()
        url = ''.join(letter for letter in to_get_url if letter.isalnum() or letter == '-')

        PracticeGame(user_id=user_info.pk, title=title, url=url).save()

        return redirect(reverse('wordbook:game_list'))


class PracticeGameListView(LoginRequiredMixin, generic.ListView):
    model = PracticeGame
    paginate_by = 10
    template_name = 'wordbook/practicegame_list.html'

    def get(self, request, *args, **kwargs):
        queryset_list = PracticeGame.objects.filter(user_id=request.user.pk, complete=False)
        paginator = Paginator(queryset_list, self.paginate_by)
        page = self.request.GET.get('page')
        queryset = paginator.get_page(page)
        context = {
            'queryset': queryset,
        }
        return render(request, 'wordbook/practicegame_list.html', context)


class PracticeGameDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = PracticeGame
    success_url = reverse_lazy('wordbook:game_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

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


class PracticeGameDetailView(LoginRequiredMixin, generic.DetailView):
    model = PracticeGame
    slug_field = 'url'

    def get_context_data(self, **kwargs):
        context = super(PracticeGameDetailView, self).get_context_data(**kwargs)
        return context
    # def get(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     if self.object.draft:
    #         raise PermissionError
    #
    #     context = self.get_context_data(object=self.object)
    #     return self.render_to_response(context)


class PracticeGamePlayView(LoginRequiredMixin, generic.FormView):
    form_class = QuestionForm
    template_name = 'wordbook/practicegame_play.html'

    def get_context_data(self, **kwargs):
        context = super(PracticeGamePlayView, self).get_context_data(**kwargs)
        return context

    def get_form_kwargs(self):
        kwargs = super(PracticeGamePlayView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


    #     # form_class = PracticeGameForm
    #     # template_name = 'wordbook/repeated_game.html'
    #     #
    #     # def post(self, request, *args, **kwargs):
    #     #     form = PracticeGameForm(request.POST)
    #     #     if not form.is_valid():
    #     #         return render(request, 'wordbook/repeated_game.html', {'form': form})
    #     #     # form.save(commit=True)
    #     #     form.save(commit=True)
    #     #     return redirect('wordbook:home')
    #
#     def get(self, request, *args, **kwargs):
#         user_info = UserManager.objects.get(username=request.user)  # ユーザー情報の取得
#
#         # PracticeGameContext(user_id=user_info.pk).save()  # PracticeGameContextテーブルにデータ作成
#         latest_game_record = PracticeGame.objects.filter(  # 一番最近に作成されたPracticeGameContextのデータの取得
#             pk=request.pk).values('pk').last()
#
#         user_word_data = Wordbook.objects.filter(user=request.user)  # ログイン中のユーザーの単語情報（単語帳に登録されている単語全て）の取得
#         user_wordbook_data = user_word_data.values('pk')  # その id 取得
#
#         # Wordbookからユーザーで絞り込んだid をランダムに１０個取得。
#         wordbook_randomly_selected = np.random.choice(list(user_wordbook_data), 10, replace=False)
#
#         list_for_wordbook_randomly_selected = []
#         # forループ内では、Questionテーブルにwordbook_randomly_selectedで取得したデータを基にデータ作成
#         for j in wordbook_randomly_selected:
#             is_wordbook_id = j['pk']
#             list_for_wordbook_randomly_selected.append(is_wordbook_id)
#             Question(wordbook_id=is_wordbook_id, practice_game_id=latest_game_record['pk']).save()
#
#         # wordbook_randomly_selectedで選出されたidで絞り込んでword_idの取得。
#         queryset_of_its_word_ids = []
#         for l in list_for_wordbook_randomly_selected:
#             its_word_ids = Wordbook.objects.filter(pk=l).values('word_id')
#             queryset_of_its_word_ids.append(its_word_ids)
#
#         list_for_word_ids_queryset = []
#         for l in queryset_of_its_word_ids:
#             for entry in l:
#                 is_word_id = entry['word_id']
#                 list_for_word_ids_queryset.append(is_word_id)
#
#         list_for_random_choices = []
#         for l in list_for_word_ids_queryset:
#             choices = Word.objects.exclude(pk=l).values('pk')
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
#         # practice_game_idで絞り込んだ、Questionの id 取得
#         question_ids = Question.objects.filter(
#             practice_game_id=latest_game_record['pk']).values('pk')
#
#         list_for_question_ids = []
#         for q in question_ids:
#             list_for_question_ids.append(q['pk'])
#
#         # 作成したquestion_idそれぞれに対応するword_idを明確にする為の辞書（combined_dict）を作成
#         combined_dict = dict(zip(list_for_question_ids, list_divided_by_3))
#
#         # combined_dictからMultipleChoicesテーブルへ保存
#         for cd in combined_dict:
#             for n in range(0, 3):
#                 MultipleChoices(question_id=cd, word_id=combined_dict[cd][n]).save()
#
#         # 保存した選択問題の取得
#         list_for_get_shown_multiple_choices_data = []
#         for l in list_for_question_ids:
#             get_shown_multiple_choices_data = MultipleChoices.objects.filter(question_id=l).values('word_id')
#             list_for_get_shown_multiple_choices_data.append(get_shown_multiple_choices_data)
#
#         list_for_after_loop = []
#         for n in range(0, len(list_for_get_shown_multiple_choices_data)):
#             for m in range(0, 3):
#                 list_for_after_loop.append(list_for_get_shown_multiple_choices_data[n][m]['word_id'])
#
#         list_for_its_loop = []
#         for n in range(0, len(list_for_after_loop)):
#             list_for_its_loop.append(list_for_after_loop[n])
#
#         group_by = 3
#         list_divided_by_3_shown = []
#         for l in [list_for_its_loop[i:i + group_by] for i in
#                   range(0, len(list_for_its_loop), group_by)]:
#             list_divided_by_3_shown.append(l)
#
#         list_for_exec_query2 = []
#         for l in list_for_question_ids:
#             list_for_exec_query2.append(MultipleChoices.exec_query2(l))
#
#         list_for_slicing = []
#         for l in list_for_exec_query2:
#             list_for_slicing.append(l[0]['word_id'])
#
#         list_for_zip = []
#         for l1, l2 in zip(list_divided_by_3_shown, list_for_slicing):
#             list_for_zip.append(l1 + [l2])
#
#         list_for_vocab_meanings = []
#         for n in range(0, len(list_for_zip)):
#             for l in list_for_zip[n]:
#                 get_vocab_meanings = Word.objects.filter(pk=l).values('vocab_meaning')
#                 list_for_vocab_meanings.append(get_vocab_meanings)
#
#         group_by2 = 4
#         shown_list = []
#         for l in [list_for_vocab_meanings[i:i + group_by2] for i in
#                   range(0, len(list_for_vocab_meanings), group_by2)]:
#             shown_list.append(l)
#
#         context = {
#             'shown_list': shown_list,
#         }
#         render(request, 'wordbook/repeated_game.html', context)
#
#
# def take_quiz(request, pk):
#     quiz = get_object_or_404(Question, pk=pk)
#     login_user = request.user
#
#     if login_user..filter(pk=pk).exists():
#             return render(request, 'students/taken_quiz.html')
#
#         total_questions = quiz.questions.count()
#         unanswered_questions = student.get_unanswered_questions(quiz)
#         total_unanswered_questions = unanswered_questions.count()
#         progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
#         question = unanswered_questions.first()
#
#         if request.method == 'POST':
#             form = TakeQuizForm(question=question, data=request.POST)
#             if form.is_valid():
#                 with transaction.atomic():
#                     student_answer = form.save(commit=False)
#                     student_answer.student = student
#                     student_answer.save()
#                     if student.get_unanswered_questions(quiz).exists():
#                         return redirect('students:take_quiz', pk)
#                     else:
#                         correct_answers = student.quiz_answers.filter(answer__question__quiz=quiz,
#                                                                       answer__is_correct=True).count()
#                         score = round((correct_answers / total_questions) * 100.0, 2)
#                         TakenQuiz.objects.create(student=student, quiz=quiz, score=score)
#                         if score < 50.0:
#                             messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (
#                             quiz.name, score))
#                         else:
#                             messages.success(request,
#                                              'Congratulations! You completed the quiz %s with success! You scored %s points.' % (
#                                              quiz.name, score))
#                         return redirect('students:quiz_list')
#         else:
#             form = TakeQuizForm(question=question)
#
#         return render(request, 'classroom/students/take_quiz_form.html', {
#             'quiz': quiz,
#             'question': question,
#             'form': form,
#             'progress': progress
#         })
#
#         return super(QuizTake, self).dispatch(request, *args, **kwargs)



    # def get_form_kwargs(self):
    #     kwargs = super(RepeatedGameView, self).get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     return kwargs
        # forを抜けた後用に空のリストを用意。

        #     # if not Question.objects.filter(wordbook=i.pk).exists():
        #     each_user_wordbook_data = Wordbook.objects.get(pk=i.pk)
        #     create_questions = Question(wordbook=each_user_wordbook_data)
        #     create_questions.save()

    # def get(self, request, *args, **kwargs):
    #     global is_game_word, is_answer
    #     # 現在ログイン中のユーザー情報から単語データを取得。
    #     user_word_data = Wordbook.objects.filter(user=request.user)
    #     # リストからランダム抽出（"word__vocab"と"word_meaning__vocab_meaning"）＆重複なし。
    #     is_randomly_selected = np.random.choice(
    #         list(user_word_data.values('word__vocab', 'word__vocab_meaning')),
    #         1,
    #         replace=False,
    #     )
    #     # for内では特定の要素の取得
    #     for j in is_randomly_selected:
    #         # 出題される単語
    #         is_game_word = j['word__vocab']
    #         # 答えである意味
    #         is_answer = j['word__vocab_meaning']
    #
    #     # ４つの選択肢のうち、答え以外の３つの取得かつ、その３つが答えと重複しないようにした。
    #     choices = Word.objects.exclude(vocab_meaning=is_answer).values('vocab_meaning')
    #     # リストからランダム抽出。重複なし。
    #     random_choices = np.random.choice(list(choices), 3, replace=False)
    #     # forを抜けた後用に空のリストを用意。
    #     list_random_choices = []
    #     # for内では残り３つの選択肢の取得。
    #     for n in range(0, 3):
    #         are_elements = random_choices[n]['vocab_meaning']
    #         # 取得したデータを空リスト内に格納。
    #         list_random_choices.append(are_elements)
    #     # 加えて、答えもその中に格納
    #     list_random_choices.append(is_answer)
    #     # ランダムに選択肢を表示する為にシャッフル。
    #     random.shuffle(list_random_choices)
    #     # choice1 ~ choice4までの定義
    #     choice1 = list_random_choices[0]
    #     choice2 = list_random_choices[1]
    #     choice3 = list_random_choices[2]
    #     choice4 = list_random_choices[3]
    #
    #     context = {
    #         'is_game_word': is_game_word,
    #         'choice1': choice1,
    #         'choice2': choice2,
    #         'choice3': choice3,
    #         'choice4': choice4,
    #     }
    #     return render(request, 'wordbook/repeated_game.html', context)
    #
    #     # def post(self, request, *args, **kwargs):
    #     #     if request.method == 'POST':
    #     #         for n in range(0, 4):
    #     #             if request




