from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,login,authenticate

# Create your views here.
@login_required
def home(req):
    return render(req,'Oas/index.html')

def user_login(req):
    if req.method == 'POST':
        user=authenticate(username=req.POST.get('username'),
                          password=req.POST.get('password'))
        if user is not None:
            login(req,user)
            return redirect('/')
        else:
            login_error = "Your username and password didn't match. Please try again."
            return render(req,'Oas/login.html',{'login_error':login_error})
    return render(req,'Oas/login.html')

def user_logout(req):
    logout(req)
    return redirect('/login/')