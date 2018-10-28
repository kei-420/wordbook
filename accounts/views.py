from django.shortcuts import render, redirect, reverse
from django.views import View
from .forms import SignUpForm, LogInForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin


class SignUpView(View):
    def get(self, request, *args, **kwargs):
        form = SignUpForm()
        return render(request, 'accounts/signup.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        if not form.is_valid():
            return render(request, 'accounts/signup.html', {'form': form})
        user_info_save = form.save(commit=True)

        # create_user_blog = Post()
        # create_user_blog.user = user_info_save
        # create_user_blog.save()

        auth_login(request, user_info_save)
        return redirect('accounts:login')


# class ConfirmUserInfo(View):
#     def get(self, request, *args, **kwargs):
#         form = SignUpForm()
#         if not form.is_valid():
#             return render(request, 'accounts/signup.html', {'form': form})
#         return render(request, 'accounts/confirm_user_info.html', {'form': form})


class LogInView(View):
    def get(self, request, *args, **kwargs):
        form = LogInForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = LogInForm(request.POST)
        if not form.is_valid():
            return render(request, 'accounts/login.html', {'form': form})

        login_user = form.get_login_user()
        auth_login(request, login_user)

        return redirect(reverse('wordbook:home'))


class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            auth_logout(request)

        return redirect(reverse('accounts:login'))