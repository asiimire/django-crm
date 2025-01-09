from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def home(request):
    if request.method == "POST":
        if 'login' in request.POST:  # If the login form is submitted
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You have successfully logged in.")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        
        elif 'register' in request.POST:  # If the registration form is submitted
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
            else:
                if User.objects.filter(username=email).exists():
                    messages.error(request, "An account with this email already exists.")
                else:
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    user.save()
                    messages.success(request, "Your account has been created successfully. Please log in.")
                    return redirect('home')

    return render(request, 'home.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('home')
