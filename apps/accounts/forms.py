from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, UserChangeForm,
    PasswordResetForm, SetPasswordForm,
)
from django.contrib.auth import authenticate
from .models import User


class RegistrationForm(UserCreationForm):
    #* После регистрации отправляется письмо с подтверждением email / After registration, a confirmation email is sent
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        }),
        label='Email'
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 123-45-67'
        }),
        label='Phone number'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('username', 'password1', 'password2'):
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class LoginForm(AuthenticationForm):
    #? Сотрудники входят только по email. TOTP-код обязателен если включена 2FA. / Staff log in only by email. TOTP code is required if 2FA is enabled.
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email (for staff) or username'
        }),
        label='Email or username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        label='Password'
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Remember me'
    )
    otp_code = forms.CharField(
        required=False,
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Code from Google Authenticator',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
            'pattern': '[0-9]*'
        }),
        label='2FA code (if enabled)'
    )

    def clean(self):
        #* 1) Ищем по email (для staff) или username. 2) Проверяем пароль. 3) Для staff — TOTP. / 1) Find by email (for staff) or username. 2) Verify password. 3) For staff — TOTP.
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        otp_code = self.cleaned_data.get('otp_code', '')

        if username and password:
            #* Пробуем найти пользователя по email, иначе по username / Try to find user by email, otherwise by username
            try:
                user = User.objects.get(email=username)
                username_field = user.username
            except User.DoesNotExist:
                username_field = username

            self.user_cache = authenticate(
                self.request,
                username=username_field,
                password=password,
            )

            if self.user_cache is None:
                raise forms.ValidationError(
                    'Invalid email/login or password.',
                    code='invalid_login',
                )

            #! Если сотрудник и 2FA включена — проверяем TOTP / If staff and 2FA is enabled — verify TOTP
            if self.user_cache.is_staff and self.user_cache.totp_secret:
                import pyotp
                totp = pyotp.TOTP(self.user_cache.totp_secret)
                if not otp_code or not totp.verify(otp_code, valid_window=1):
                    raise forms.ValidationError(
                        'Invalid two-factor authentication code.',
                        code='invalid_otp',
                    )
        return self.cleaned_data


class ProfileForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = (
            'username', 'email', 'phone',
            'first_name', 'last_name', 'birthday', 'avatar'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['avatar'].widget.attrs.pop('class', None)


class StaffCreationForm(UserCreationForm):
    #* Только админ может создавать сотрудников через эту форму / Only admin can create staff members through this form
    is_staff = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Admin panel access'
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'phone',
            'first_name', 'last_name',
            'is_staff', 'password1', 'password2'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if not isinstance(self.fields[field_name].widget, forms.CheckboxInput):
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})


#? Переопределяем стандартные формы сброса пароля для Bootstrap-стилей / Override standard password reset forms for Bootstrap styling
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email'
        }),
        label='Email'
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        }),
        label='New password'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        }),
        label='Password confirmation'
    )
