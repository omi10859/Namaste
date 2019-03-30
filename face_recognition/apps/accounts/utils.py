from apps.core.utils import getOption
from apps.email_app.schedulers import ScheduleEmail
from django.contrib.auth.tokens import (PasswordResetTokenGenerator,
                                        default_token_generator)
from django.db.models.fields.reverse_related import ManyToOneRel, OneToOneRel
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils import six
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rolepermissions.roles import assign_role

from .models import User
from .roles import Subscriber


def UserExistsByEmail(email):
    try:
        return User.objects.get(email = email)
    except User.DoesNotExist:
        return False

def sendPasswordResetEmail(user_email):

    user = UserExistsByEmail(user_email)
    if not user:
        return False
    
    context = {
        'user': user,
        'domain': getOption('site_url'),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'token': PasswordResetTokenGenerator().make_token(user),
        'protocol': 'http'
    }

    subject = "Reset your Password"

    html = render_to_string("accounts/email/forgot-password/template.html", context=context)
    text = render_to_string("accounts/email/forgot-password/template.txt", context=context)

    ScheduleEmail(to_email=user.email, subject=subject, html_text=html, plain_text=text)
    
    return True

def ActivateUserAccount(user):
    try:
        user.email_confirmed = True
        user.save()
        return True
    except Exception:
        return False

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.email_confirmed)
        )

def SendAccountActivationEmail(user_email):
    
    user = UserExistsByEmail(user_email)
    if not user:
        return False

    context = {
        'user': user,
        'domain': getOption('site_url'),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'token': AccountActivationTokenGenerator().make_token(user)
    }

    subject = "Activate your account"

    html = render_to_string("accounts/email/signup/template.html", context=context)
    text = render_to_string("accounts/email/signup/template.txt", context=context)

    ScheduleEmail(to_email=user.email, subject=subject, html_text=html, plain_text=text)

    context = {
        'user': user
    }
    html = render_to_string("accounts/email/signup-admin/template.html", context=context)
    text = render_to_string("accounts/email/signup-admin/template.txt", context=context)

    ScheduleEmail(to_email=getOption('new_account_email_to_address'), subject="New User Signup at GSTHEALTH", html_text=html, plain_text=text)

    return True

def DoPostAccountCreation(user):
    assign_role(user, Subscriber)
