"""
URL routes for the accounts app.

Includes:
- Registration / Login / Logout
- Email confirmation
- Password reset (Django built-in)
- 2FA (TOTP) setup
- Staff management (admin only)
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

app_name = 'accounts'

urlpatterns = [
    # ─── Registration & Login ───
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),

    # ─── Email Confirmation ───
    path('confirm-email/<uidb64>/<token>/', views.confirm_email, name='confirm_email'),
    path('resend-confirmation/', views.resend_confirmation, name='resend_confirmation'),

    # ─── Password Reset (Django generic) ───
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset_form.html',
            form_class=CustomPasswordResetForm,
            email_template_name='accounts/email/password_reset.txt',
            subject_template_name='accounts/email/password_reset_subject.txt',
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            form_class=CustomSetPasswordForm,
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),

    # ─── 2FA (Google Authenticator) ───
    path('otp/setup/', views.otp_setup, name='otp_setup'),
    path('otp/disable/', views.otp_disable, name='otp_disable'),

    # ─── Staff Management (superuser only) ───
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/create/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/otp/', views.staff_otp_show, name='staff_otp_show'),
    path('staff/<int:pk>/reset-otp/', views.staff_reset_otp, name='staff_reset_otp'),

    # ─── HR: Employee Documents ───
    path('hr/employees/', views.employee_list, name='employee_list'),
    path('hr/employees/<int:pk>/', views.employee_detail, name='employee_detail'),
]
