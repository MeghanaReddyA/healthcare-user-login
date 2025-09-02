from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Profile


def signup_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        line1 = request.POST.get("line1")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode")
        user_type = request.POST.get("user_type")
        profile_picture = request.FILES.get("profile_picture")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("signup")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        profile = Profile.objects.create(
            user=user,
            line1=line1,
            city=city,
            state=state,
            pincode=pincode,
            user_type=user_type,
            profile_picture=profile_picture
        )

        user.save()
        profile.save()

        messages.success(request, "Signup successful! Please login.")
        return redirect("login")

    return render(request, "accounts/signup.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "accounts/login.html")


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    profile = Profile.objects.get(user=request.user)

    context = {
        "user": request.user,
        "profile": profile,
    }
    return render(request, "accounts/dashboard.html", context)

def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out successfully")
    return redirect("login")
