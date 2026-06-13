import base64
import os

from django.contrib.auth.models import AbstractUser
from django.db  import models
from django.utils.translation  import gettext_lazy as _


class User(AbstractUser):
    # roles: superuser, expansion_manager, hr_manager, staff, buyer
    phone = models.CharField(
        _('Phone'), max_length=20, blank=True,
        help_text='Format: +44 77 1234 5678'
    )
    avatar = models.ImageField(
        _('Avatar'), upload_to='users/avatars/', blank=True, null=True
    )
    birthday = models.DateField(
        _('Birthday'), blank=True, null=True
    )
    email_confirmed = models.BooleanField(
        _('Email confirmed'), default=False,
        help_text='Set to True after user clicks the confirmation link'
    )
    #! empty totp_secret means 2FA is off. Cleared when disabling.
    totp_secret = models.CharField(
        _('TOTP secret'), max_length=64, blank=True,
        help_text='Base32 key for Google Authenticator. Empty = 2FA disabled.'
    )
    is_expansion_manager = models.BooleanField(
        _('Expansion manager'), default=False,
        help_text='Can create/edit stores and assign store staff'
    )
    #* HR manager: manages employee documents, right-to-work checks, payroll info
    is_hr_manager = models.BooleanField(
        _('HR manager'), default=False,
        help_text='Can manage employee profiles, documents, and payroll details'
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.get_full_name() or self.username

    def get_totp_secret(self):
        if not self.totp_secret:
            self.totp_secret = base64.b32encode(os.urandom(20)).decode('utf-8')
            self.save(update_fields=['totp_secret'])
        return self.totp_secret

    @property
    def is_admin(self):
        return self.is_superuser

    @property
    def is_employee(self):
        return self.is_staff

    @property
    def is_exp_manager(self):
        return self.is_expansion_manager or self.is_superuser

    @property
    def is_hr(self):
        return self.is_hr_manager or self.is_superuser

    def can_manage_staff(self):
        return self.is_superuser

    def can_manage_stores(self):
        return self.is_expansion_manager or self.is_superuser

    def can_assign_store_staff(self):
        return self.is_expansion_manager or self.is_superuser

    def can_manage_hr(self):
        #* HR manager or superuser can manage employee documents/payroll
        return self.is_hr_manager or self.is_superuser


class EmployeeProfile(models.Model):
    #! employment documents: passport, right-to-work, NI/SSN, bank, emergency contact
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='employee_profile',
        verbose_name=_('User')
    )
    # identity
    passport_number = models.CharField(
        _('Passport number'), max_length=50, blank=True,
        help_text='Passport number or national ID card number'
    )
    right_to_work = models.FileField(
        _('Right to work document'), upload_to='hr/right_to_work/',
        blank=True, null=True,
        help_text='Visa, BRP, share code screenshot, or work authorisation'
    )
    # tax / social
    ni_number = models.CharField(
        _('NI / SSN'), max_length=20, blank=True,
        help_text='National Insurance (UK) or Social Security Number (US)'
    )
    # address
    proof_of_address = models.FileField(
        _('Proof of address'), upload_to='hr/address/',
        blank=True, null=True,
        help_text='Utility bill or bank statement (last 3 months)'
    )
    # emergency contact
    emergency_name = models.CharField(
        _('Emergency contact name'), max_length=100, blank=True
    )
    emergency_phone = models.CharField(
        _('Emergency contact phone'), max_length=30, blank=True
    )
    emergency_relationship = models.CharField(
        _('Relationship'), max_length=50, blank=True,
        help_text='e.g. spouse, parent, sibling'
    )
    # payroll
    bank_name = models.CharField(
        _('Bank name'), max_length=100, blank=True
    )
    bank_account_number = models.CharField(
        _('Account number'), max_length=30, blank=True,
        help_text='Bank account number'
    )
    bank_sort_code = models.CharField(
        _('Sort code / Routing'), max_length=20, blank=True,
        help_text='Sort code (UK) or routing number (US)'
    )
    # job
    job_title = models.CharField(
        _('Job title'), max_length=100, blank=True
    )
    department = models.CharField(
        _('Department'), max_length=100, blank=True
    )
    start_date = models.DateField(
        _('Start date'), blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Employee profile')
        verbose_name_plural = _('Employee profiles')

    def __str__(self):
        return f'Employee: {self.user.get_full_name() or self.user.username}'
