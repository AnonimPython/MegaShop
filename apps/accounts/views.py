import os
import pyotp
import qrcode
import qrcode.image.svg
import qrcode.image.pil
import base64

from io import BytesIO

from django.conf import settings
from config import logger
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_POST

from .forms import (
    RegistrationForm, LoginForm, ProfileForm,
    StaffCreationForm,
)
from .models import User

UserModel = get_user_model()

# ─── Регистрация и вход / Registration & Login ───

def register(request):
    #* Регистрация / Registration: create user, send confirmation email
    #* Register: create user, send email confirmation, auto-login
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():

            user = form.save(commit=False)
            user.is_staff = False
            user.email_confirmed = False
            user.save()

            logger.info(
                f'New user: {user.username} <{user.email}>'
            )

            #* Отправляем письмо только обычным юзерам
            #* Send confirmation only for regular users
            send_confirmation_email(request, user)

            login(request, user)
            messages.success(
                request,
                'Registration successful! Check your email for confirmation.'
            )
            return redirect('catalog:product_list')

    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    #? Для staff: вход только по email + TOTP (если 2FA включена)
    #? Staff: login via email + TOTP (if 2FA is enabled)
    #? После входа: если 2FA не настроена — редирект на её настройку
    #? If 2FA is not configured — redirect to setup page
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            login(request, user)

            logger.info(
                f'Login: {user.username} (staff={user.is_staff})'
            )

            #* "Запомнить меня" = сессия на 30 дней, иначе на 7
            #* Remember me = 30 days, otherwise 7
            remember_me = form.cleaned_data.get('remember_me', False)
            if remember_me:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE_REMEMBER)
            else:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE_DEFAULT)

            #! Сотрудник без 2FA — предлагаем настроить принудительно
            #! Staff without 2FA — forced redirect to setup
            if user.is_staff and not user.totp_secret:
                messages.warning(
                    request,
                    'Set up two-factor authentication to access the admin panel.'
                )
                return redirect('accounts:otp_setup')

            messages.success(
                request,
                f'Welcome, {user.get_full_name() or user.username}!'
            )
            return redirect(request.GET.get('next', 'catalog:product_list'))
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile(request):
    #* Редактирование профиля: имя, email, телефон, аватар, дата рождения
    #* Edit profile: name, email, phone, avatar, birthday
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


# ─── Подтверждение email / Email Confirmation ───

def send_confirmation_email(request, user):
    #* Формируем ссылку с uid + token, отправляем письмо
    #* Build uid + token URL, send the email
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    confirm_url = request.build_absolute_uri(
        reverse('accounts:confirm_email', args=[uid, token])
    )

    subject = 'Email confirmation — MegaShop'
    message = render_to_string('accounts/email/confirm_email.txt', {
        'user': user,
        'confirm_url': confirm_url,
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def confirm_email(request, uidb64, token):
    #* Проверяет uid + token, подтверждает email
    #* Verify uid + token, confirm email
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.email_confirmed = True
        user.save(update_fields=['email_confirmed'])
        messages.success(request, 'Email confirmed successfully!')
    else:
        messages.error(request, 'Confirmation link is invalid.')

    return redirect('catalog:product_list')


def resend_confirmation(request):
    #* Повторная отправка письма подтверждения
    #* Resend confirmation email
    if request.user.is_authenticated and not request.user.email_confirmed:
        send_confirmation_email(request, request.user)
        messages.success(request, 'Confirmation email resent.')

    return redirect('accounts:profile')


# ─── 2FA (Google Authenticator) ───

@login_required
@user_passes_test(lambda u: u.is_staff)
def otp_setup(request):
    user = request.user

    if user.totp_secret and request.method == 'GET':
        messages.info(request, '2FA is already enabled.')
        return redirect('admin_panel:dashboard')

    #* store temporary secret in session (persist between GET and POST)
    if request.method == 'GET':
        secret = base64.b32encode(os.urandom(20)).decode('utf-8')
        request.session['_otp_tmp_secret'] = secret
    else:
        secret = request.session.get('_otp_tmp_secret')
        if not secret:
            messages.error(request, 'Session expired, scan QR again.')
            return redirect('accounts:otp_setup')

    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name=settings.OTP_TOTP_ISSUER,
    )

    qr = qrcode.make(uri, image_factory=qrcode.image.pil.PilImage)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    qr_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    qr_base64 = f'data:image/png;base64,{qr_data}'

    if request.method == 'POST':
        code = request.POST.get('code', '')
        totp = pyotp.TOTP(secret)
        if totp.verify(code, valid_window=1):
            user.totp_secret = secret
            user.save(update_fields=['totp_secret'])
            del request.session['_otp_tmp_secret']
            messages.success(request, 'Two-factor authentication enabled!')
            return redirect('admin_panel:dashboard')
        else:
            messages.error(request, 'Invalid code, try again.')

    return render(request, 'accounts/otp_setup.html', {
        'qr_base64': qr_base64,
        'secret': secret,
        'uri': uri,
    })


@login_required
@require_POST
def otp_disable(request):
    #! Отключаем 2FA только после подтверждения паролем
    #! Disable 2FA only after password confirmation
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('catalog:product_list')

    password = request.POST.get('password', '')
    user = authenticate(
        request,
        username=request.user.username,
        password=password,
    )
    if user is not None:
        user.totp_secret = ''
        user.save(update_fields=['totp_secret'])
        messages.success(request, 'Two-factor authentication disabled.')
    else:
        messages.error(request, 'Invalid password.')

    return redirect('accounts:profile')


# ─── Сотрудники / Staff Management (только суперпользователь) ───

@login_required
@user_passes_test(lambda u: u.is_superuser)
def staff_list(request):
    #* Список всех сотрудников для управления
    #* List all staff users for management
    staff_users = UserModel.objects.filter(is_staff=True).annotate(
        orders_handled=Count('orders')
    )
    return render(
        request, 'accounts/staff_list.html', {'staff_users': staff_users}
    )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def staff_create(request):
    #* Создание нового сотрудника. Только админ.
    #* Create new staff. Admin only.
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = False
            user.email_confirmed = True  #! Сотрудникам не нужно подтверждение email / Staff don't need email confirmation

            #* Генерируем TOTP-секрет / Generate TOTP secret immediately to show QR code to admin
            #! Сотрудник получит секрет от админа / Staff receives secret from admin, not via email
            user.totp_secret = base64.b32encode(os.urandom(20)).decode('utf-8')
            user.save()

            logger.info(
                f'Staff created: {user.username} <{user.email}> '
                f'(by admin: {request.user.username})'
            )

            #? Письмо не шлём — только 2FA через Google Authenticator
            #? No email — only Google Authenticator 2FA

            return redirect('accounts:staff_otp_show', pk=user.pk)
    else:
        form = StaffCreationForm()

    return render(request, 'accounts/staff_form.html', {
        'form': form, 'title': 'Create staff account',
    })


# ─── HR: Employee Profile / Documents ───

@login_required
@user_passes_test(lambda u: u.is_hr_manager or u.is_superuser)
def employee_list(request):
    # list all staff with their hr profile status
    from django.db.models import Count, Q
    employees = UserModel.objects.filter(is_staff=True).annotate(
        orders_handled=Count('orders'),
        has_hr_profile=Count('employee_profile'),
    )
    # hr managers see everyone; superusers see everyone
    return render(
        request, 'accounts/hr/employee_list.html',
        {'employees': employees}
    )


@login_required
@user_passes_test(lambda u: u.is_hr_manager or u.is_superuser)
def employee_detail(request, pk):
    from .models import EmployeeProfile
    user = get_object_or_404(UserModel, pk=pk, is_staff=True)
    profile, created = EmployeeProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        #? update employee profile fields
        profile.passport_number = request.POST.get('passport_number', '')
        profile.ni_number = request.POST.get('ni_number', '')
        profile.bank_name = request.POST.get('bank_name', '')
        profile.bank_account_number = request.POST.get('bank_account_number', '')
        profile.bank_sort_code = request.POST.get('bank_sort_code', '')
        profile.emergency_name = request.POST.get('emergency_name', '')
        profile.emergency_phone = request.POST.get('emergency_phone', '')
        profile.emergency_relationship = request.POST.get('emergency_relationship', '')
        profile.job_title = request.POST.get('job_title', '')
        profile.department = request.POST.get('department', '')

        start_date_str = request.POST.get('start_date', '')
        if start_date_str:
            from datetime import datetime
            try:
                profile.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass

        # file uploads
        if 'right_to_work' in request.FILES:
            profile.right_to_work = request.FILES['right_to_work']
        if 'proof_of_address' in request.FILES:
            profile.proof_of_address = request.FILES['proof_of_address']

        profile.save()
        messages.success(request, 'Employee profile updated.')
        return redirect('accounts:employee_detail', pk=user.pk)

    return render(request, 'accounts/hr/employee_detail.html', {
        'employee': user, 'profile': profile,
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def staff_otp_show(request, pk):
    #! Показывает QR-код для сотрудника. Доступно только суперадмину.
    #! Shows TOTP QR code. Only superadmin can see.
    user = get_object_or_404(UserModel, pk=pk, is_staff=True)
    secret = user.totp_secret
    if not secret:
        messages.error(request, '2FA is not configured for this employee.')
        return redirect('accounts:staff_list')

    #* Генерируем QR-код как PNG base64
    #* Generate PNG base64 QR code
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email or user.username,
        issuer_name=settings.OTP_TOTP_ISSUER,
    )
    qr = qrcode.make(uri, image_factory=qrcode.image.pil.PilImage)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    qr_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    qr_base64 = f'data:image/png;base64,{qr_data}'

    return render(request, 'accounts/staff_otp_show.html', {
        'staff_user': user, 'qr_base64': qr_base64, 'secret': secret,
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_POST
def staff_reset_otp(request, pk):
    #* Сброс TOTP для сотрудника, генерация нового секрета
    #* Reset TOTP for staff, generate new secret
    user = get_object_or_404(UserModel, pk=pk, is_staff=True)
    user.totp_secret = base64.b32encode(os.urandom(20)).decode('utf-8')
    user.save(update_fields=['totp_secret'])
    logger.info(
        f'TOTP reset for {user.username} (by admin: {request.user.username})'
    )
    messages.success(
        request,
        f'2FA reset for {user.get_full_name() or user.username}'
    )
    return redirect('accounts:staff_otp_show', pk=user.pk)
