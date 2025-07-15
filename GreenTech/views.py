from audioop import add
from curses import use_default_colors
import email
from email.message import EmailMessage
from tokenize import generate_tokens
from unicodedata import name
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from Iads import settings
from GreenTech.models import SignupFields
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from Iads.tokens import generate_token
from django.core.mail import EmailMessage, send_mail
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.decorators import login_required
from .decorators import *


# Create your views here.

@unauthenticated_user
def signup(request):
    if request.method == "POST":
        Name = request.POST['Name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if User.objects.filter(username=Name):
            messages.error(request, "Username already exists", extra_tags="validation")
            return redirect('/signup')

        if User.objects.filter(email=email):
            messages.error(request, "Email already exists", extra_tags="validation")
            return redirect('/signup')

        if password != confirm_password:
            messages.error(request, "Password does not match", extra_tags="validation")
            return redirect('/signup')

        if not Name.isalnum():
            messages.error(request, "Username should only contain letters and numbers", extra_tags="validation")
            return redirect('/signup')

        myuser = User.objects.create_user(Name, email, password)
        myuser.first_name = Name
        myuser.email = email
        myuser.is_active = False
        myuser.save()
        address = request.POST.get('address')
        number = request.POST.get('number')
        age = request.POST.get('age')
        data1 = SignupFields(name=Name, address=address, number=number, age=age)
        data1.save()

        messages.success(request, "Your account has been successfully created Check mail to verify.",
                         extra_tags="valid")

        # welcome email
        subject = "Welcome to Complaint Management System"
        message = "Hi " + myuser.first_name + "! Welcome to Complaint Management System!!!.\n We are glad to have you here!!!.\nWe have sent you a confirmation email to " + myuser.email + ".\nPlease confirm your email to continue using our services.\n\nThank You!!!"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # confirmation email
        current_site = get_current_site(request)
        email_subject = "Confirm your email"
        message2 = render_to_string('email_confirmation.html', {
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email]
        )
        email.fail_silently = True
        email.send()

        return redirect('/')

    return render(request, "GreenTech/signup.html")


@unauthenticated_user
def signin(request):
    if (request.method == "POST"):
        Name = request.POST['Name']
        password = request.POST['Password']
        user = authenticate(username=Name, password=password)
        if Name == 'root' and password == 'root':
            login(request, user)
            return redirect('/admins')

        if user is not None:
            login(request, user)
            return redirect('/home')

        else:
            validate = User.objects.filter(username=Name).exists()
            if validate:
                messages.error(request, "Invalid Password", extra_tags="pass")
                return redirect('/')
            else:
                messages.error(request, "Invalid Username", extra_tags="user")
                return redirect('/')
    return render(request, "greenTech/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out", extra_tags="logout")
    return redirect('/')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('/home')
    else:
        return render(request, 'activation_failed.html')


@login_required(login_url='signin')
def home(request):
    user = User.objects.all()
    context = {"users": user}
    return render(request, "greenTech/index.html", context)


@login_required(login_url='signin')
def account(request,pk):
        if request.user.is_authenticated:
            name=request.user
            user1=SignupFields.objects.filter(name=name)
            context={"users":user1}
            return render(request,"GreenTech/account.html",context)
        else:
            return redirect('/')
# @login_required(login_url='signin')
# def dashboard(request):
#     context = {}
#     user = User.objects.all()
#     context["users"] = user
#     context["Water"] = Complaint.objects.filter(name=request.user, cname='Water').count()
#     context["Light"] = Complaint.objects.filter(name=request.user, cname='Light').count()
#     context["Clean"] = Complaint.objects.filter(name=request.user, cname='Clean').count()
#     context["Other"] = Complaint.objects.filter(name=request.user, cname='Other').count()
#     return render(request, "greenTech/dashboard.html", context)