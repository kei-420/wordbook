from django import forms
from .models import UserManager
from django.contrib.auth.forms import UsernameField
from django.core.exceptions import ObjectDoesNotExist


class SignUpForm(forms.ModelForm):
    class Meta:
        model = UserManager
        fields = ('username', 'email', 'password', )
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'password'}),
        }

    confirm_password = forms.CharField(
        label='確認用パスワード',
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'confirm password'}),
    )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs = {'placeholder': 'username'}
        self.fields['email'].required = True
        self.fields['email'].widget.attrs = {'placeholder': 'email'}
        # self.fields['password'].widget.attrs = {'placeholder': 'password'}

    def clean_username(self):
        """usernameのバリデーション"""
        username = self.cleaned_data['username']
        # usernameは3文字以上にならねばエラー表示。
        if len(username) < 3:
            raise forms.ValidationError('Username must be longer than 3')
        # usernameがアルファベットを含んでなければエラー表示。
        if not username.isalpha():
            raise forms.ValidationError('Username must contain alphabets')
        # usernameが数字だけであればエラー表示。
        if username.isnumeric():
            raise forms.ValidationError('Username cannot be only numbers')
        # usernameは数字のみではならない。
        if username.isnumeric():
            raise forms.ValidationError('Username cannot contain only numbers')
        return username

    def clean(self):
        """passwordとconfirm_passwordのバリデーション"""
        super(SignUpForm, self).clean()
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        # password と confirm_passwordが一致していなければエラー表示
        if password != confirm_password:
            raise forms.ValidationError("password and confirmed_password don't match")

    def save(self, commit=True):
        """passwordをハッシュ化してからユーザー情報の保存"""

        user_info = super(SignUpForm, self).save(commit=False)
        user_info.set_password(self.cleaned_data["password"])
        if commit:
            user_info.save()

        return user_info


class LogInForm(forms.Form):
    username = UsernameField(
        label='username',
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'username',
                                      'autofocus': True})
    )
    """ -> render_value=True > ログイン画面に戻った際にパスワードが入力された状態のまま。
        -> strip=False > True（Default）の場合、値は先頭と末尾の空白を取り除かれる。"""
    password = forms.CharField(
        label='password',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'password'}, render_value=True)
    )

    def __init__(self, *args, **kwargs):
        super(LogInForm, self).__init__(*args, **kwargs)
        # ユーザー情報を保持する為のオブジェクト生成。
        self.user_request_to_login = None

    def clean_password(self):
        """Validation for password"""
        password = self.cleaned_data['password']
        return password

    def clean_username(self):
        """Validation for username"""
        username = self.cleaned_data['username']
        return username

    def clean(self):
        """Validation username corresponding to its password that was saved in Sign-Up."""
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        try:
            requesting_user = UserManager.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Input the correct username. ')
        if not requesting_user.check_password(password):
            raise forms.ValidationError('Input the correct password.')
        self.user_request_to_login = requesting_user

    def get_login_user(self):
        """ユーザ名、データベースIDなどを表す引数 user_id をとり、対応するUserオブジェクトを返す。"""
        return self.user_request_to_login
