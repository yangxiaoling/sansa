from django.shortcuts import render, redirect
from lady import models
from django import forms
from django.forms import widgets
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.


def acc_login(request):
    errors = {}
    if request.method == 'POST':
        _email = request.POST.get("email")
        _password = request.POST.get("password")
        user = authenticate(username=_email, password=_password)  # 认证
        if user:
            login(request, user)  # 登陆
            next_url = request.GET.get("next", "/crm/")  # 跳转地址
            return redirect(next_url)
        else:
            errors['error'] = "Wrong username or password!"

    return render(request, 'login.html', {'errors': errors})


@login_required
def acc_logout(request):
    logout(request)  # 登出
    return redirect('/accounts/login')


@login_required
def index(request):
    return render(request, 'index.html')