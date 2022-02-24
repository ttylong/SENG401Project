from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages

# View Functions
def index(request):
    if request.method == 'POST':
        if request.POST.get("login_s"):
            return redirect('login')
        if request.POST.get("register_s"):
            return redirect("register")
    else:
        return render(request, 'index.html')

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.info(request, "The Username and/or Password entered are incorrect!")
            return redirect("login")
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pass']
        verifypass = request.POST['confirmpass']
        email = request.POST['email']

        if password == verifypass:
            # User is the thing being imported, filter goes in the db and checks 
            # if the email entered already exists.
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already in use! Please go back and log in!")
                # Send em back to register
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username not available! Try a different one!")
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                return redirect('login')
        else:
            messages.info(request, "Passwords did not match!")
            return redirect('register')

    else:
        return render(request, 'register.html')

def home(request):
    return render(request, 'homepage.html')