from django.shortcuts import render, redirect, HttpResponse

# Authentication related imports
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import uuid
from django.contrib.sessions.models import Session
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
########################################################
from django.contrib.auth.views import LoginView
from tracker.models import Userprofile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
# Create your views here.


# Email settings

from django.conf import settings
from django.core.mail import send_mail


def home(request):
    return render(request, 'tracker/home.html')


# def loginPage(request):

#     return render(request, 'tracker/login.html')


# def handleLogin(request):
#     if request.method == 'POST':
#         loginusername = request.POST['lusername']
#         loginpassword = request.POST['pass']

#         user = authenticate(username=loginusername, password=loginpassword)

#         if user is not None:
#             login(request, user)
#             messages.success(request, "Succesfully logged in")
#             request.session['is_logged'] = True

#             return redirect('home')
#         else:
#             messages.error(request, "Invalid credentials, Please try again")
#             return redirect('home')
#     else:
#         return HttpResponse("404 - Not Found")


# class CustomLoginView(LoginView):
#     template_name = 'tracker/login.html'
#     fields = '__all__'

#     redirect_authenticated_user = True

#     def get_success_url(self):

#         messages.success(
#             self.request, "You are successfully Loged In.")
#         return reverse_lazy('home')


def login_attempt(request):

    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pass1')

        user_obj = User.objects.filter(username=username).first()
        if user_obj is None:
            messages.error(request, 'User not found.')
            return redirect('/accounts/login')

        profile_obj = Userprofile.objects.filter(user=user_obj).first()

        if not profile_obj.is_verified:
            messages.error(
                request, 'Profile is not verified check your mail.')
            return redirect('/accounts/login')

        user = authenticate(username=username, password=password)
        if user is None:
            messages.success(request, 'Wrong password.')
            return redirect('/accounts/login')

        login(request, user)
        messages.success(request, "You are successfully Loged In.")
        return redirect('home')

    return render(request, 'tracker/login.html')


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'tracker/register.html')


def handleRegister(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if len(username) > 10:
            messages.error(
                request, "username should be less than 10 characters")
            return redirect('register')
        if User.objects.filter(username=username).first():
            messages.error(request, 'Username is taken.')
            return redirect('register')

        if not username.isalnum():

            messages.error(request, "username should be alphanumeric")
            return redirect('register')
        # if User.objects.filter(email=email).first():
        #     messages.error(request, 'Email is taken.')
        #     return redirect('register')
        for c in username:
            if c.isupper():

                messages.error(request, "username should be in lower case")
                return redirect('register')
                break

        if pass1 != pass2:
            messages.error(request, "Passwords dit not match")
            return redirect('register')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = first_name
        myuser.last_name = last_name
        myuser.save()
        auth_token = str(uuid.uuid4())
        print(auth_token)
        profile_obj = Userprofile.objects.create(
            user=myuser, auth_token=auth_token)
        profile_obj.save()
        send_mail_after_registration(myuser.email, auth_token)
        # Userprofile.objects.get(user=request.user,)

        messages.success(
            request, "Your System of Reckoning account has been created successfully.")
        messages.warning(
            request, "Account verification mail has been sent to your mail")

        # Registration mail
        subject = 'WELCOME TO SYSTEM Of RECKONING!!!'
        message = f'Hi {myuser.first_name} {myuser.last_name},\n thank you for registering in System of Reckoning.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [myuser.email]
        send_mail(subject, message, email_from, recipient_list)

        user = authenticate(username=username, password=pass1)
        # if user is not None:
        #     login(request, user)
        return redirect('home')
    else:
        return HttpResponse("404 - Not Found")


def send_mail_after_registration(email, token):
    subject = 'Your accounts need to be verified'
    message = f'Hi paste the link to verify your account http://127.0.0.1:8000/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


def verify(request, auth_token):
    try:
        profile_obj = Userprofile.objects.filter(auth_token=auth_token).first()

        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                return redirect('/accounts/login')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('/accounts/login')
        else:
            messages.error(request, 'Your account needs to be verified.')
            return redirect('home')
    except Exception as e:
        print(e)
        return redirect('/')


def handleLogout(request):
    # del request.session['is_logged']
    logout(request)

    messages.success(request, "Succesfully logged out")
    return redirect("index")
