import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import phonenumbers
from .models import PhoneNumber

from RequestEvaluation.models import EvaluateRequest
from .tokens import generate_token

from Lovejoy import settings


# Create your views here.
def home(request):
    if request.user.is_superuser:
        evaluation_requests = EvaluateRequest.objects.all()
        dict_obj = {'evaluation_requests': evaluation_requests}
        return render(request, 'authentication/index.html', dict_obj)
    return render(request, 'authentication/index.html')


def signup(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['pass']
        retype_password = request.POST['re_pass']

        if User.objects.filter(username=name):
            messages.error(request, "Username already exists!")
            return redirect('signup')

        if len(name) > 10:
            messages.error(request, "Username must be under 10 characters")
            return redirect('signup')

        if not name.isalnum():
            messages.error(request, "Username must be Alpha-Numeric")
            return redirect('signup')

        if User.objects.filter(email=email):
            messages.error(request, "Email already registered!")
            return redirect('signup')

        parse_phone = phonenumbers.parse(phone, "UK")
        if not phonenumbers.is_possible_number(parse_phone):
            messages.error(request, "Phone should be in format!")
            return redirect('signup')

        if password != retype_password:
            messages.error(request, "Passwords didn't matched")
            return redirect('signup')

        password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
        if re.match(password_pattern, password) is None:
            messages.error(request, "Password requirements failed")
            return redirect('signup')

        my_user = User.objects.create_user(username=name, email=email, password=password)
        my_user.is_active = False
        my_user.save()

        user = User.objects.get(username=name)
        PhoneNumber.objects.create(user=user, phone=phone)

        # welcome email
        subject = "Welcome to LoveJoy"
        message = "Hello " + my_user.username + "!! \n Welcome to LoveJoy!! \n Thank you for visiting our website \n " \
                                                "We have also sent you a confirmation email, please confirm your " \
                                                "email to activate your account. \n\n Team LoveJoy "

        from_email = settings.EMAIL_HOST_USER
        to_list = [my_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # confirmation email
        current_site = get_current_site(request)
        email_subject = "Confirm your email @ LoveJoy"
        message2 = render_to_string('email_confirmation.html', {
            'name': my_user.username,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(my_user.pk)),
            'token': generate_token.make_token(my_user)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [my_user.email]
        )
        email.fail_silently = True
        email.send()

        messages.success(request,
                         "Your Account has been created Successfully. We have sent you a confirmation email. Use "
                         "activation link to activate your account.")

        return redirect('signup')
    return render(request, 'authentication/SignUp.html')


def signin(request):
    if request.method == "POST":
        name = request.POST['name']
        password = request.POST['pass']

        user = authenticate(username=name, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Bad Credentials")
            return redirect('signin')
    return render(request, 'authentication/SignIn.html')


def signout(request):
    logout(request)
    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return render(request, 'authentication/index.html')
    else:
        return render(request, 'activation_failed.html')


def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']
        my_user = User.objects.get(email=email)
        if my_user is not None:

            # confirmation email
            current_site = get_current_site(request)
            email_subject = "Reset your Password @ LoveJoy"
            message2 = render_to_string('Reset_Password_Link.html', {
                'name': my_user.username,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(my_user.pk)),
                'token': generate_token.make_token(my_user)
            })
            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [my_user.email]
            )
            email.fail_silently = True
            email.send()

            messages.success(request,
                             "Password reset link have been sent to your email address. Use the link to reset your "
                             "password.")
            return redirect('signin')
        else:
            messages.error(request, "Your email didn't belong to any account. Kindly submit a valid email address or "
                                    "SigUp for the new account.")

    return render(request, 'authentication/Forgot_Password.html')


def reset_password(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        return render(request, 'authentication/Reset_Password.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.success(request, 'Your link is not working, please try again later.')
        return redirect('signin')


def update_password(request):
    if request.method == "POST":
        uidb64 = request.POST['uidb64']
        token = request.POST['token']

        password = request.POST['pass']
        retype_password = request.POST['re_pass']

        if password != retype_password:
            messages.error(request, "Passwords didn't matched")
            return redirect('reset_password', uidb64=uidb64, token=token)

        password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
        if re.match(password_pattern, password) is None:
            messages.error(request, "Password validation failed")
            return redirect('reset_password', uidb64=uidb64, token=token)

        # extract user base on uid
        uid = force_text(urlsafe_base64_decode(uidb64))
        my_user = User.objects.get(pk=uid)
        my_user.set_password(password)
        my_user.save()

        # welcome email
        subject = "Password Reset Complete"
        message = "Hello " + my_user.username + "!! \n Your password has been set. \n You may go head and login now. " \
                                                "\n\n The LoveJoy Team "
        from_email = settings.EMAIL_HOST_USER
        to_list = [my_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        messages.success(request,
                         "Your Password has been change successfully.")

    return redirect('signin')
