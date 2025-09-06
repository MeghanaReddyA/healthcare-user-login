from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Profile, BlogPost
from .forms import BlogPostForm
from django.contrib.auth.decorators import login_required

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
            profile = Profile.objects.get(user=user)
            
            if profile.user_type == "doctor":
                return redirect("doctor_dashboard")
            else:
                return redirect("patient_dashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out successfully")
    return redirect("login")

@login_required
def doctor_dashboard(request):
    posts = BlogPost.objects.filter(doctor=request.user)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.doctor = request.user
            blog.save()
            return redirect('doctor_dashboard')
    else:
        form = BlogPostForm()
    
    context = {'form': form, 'posts': posts}
    return render(request, 'accounts/doctor_dashboard.html', context)

@login_required
def patient_dashboard(request):
    profile = Profile.objects.get(user=request.user)
    
    categories = [choice[0] for choice in BlogPost.CATEGORY_CHOICES]
    
    selected_category = request.GET.get('category')
    
    if selected_category:
        posts = BlogPost.objects.filter(is_draft=False, category=selected_category)
    else:
        posts = BlogPost.objects.filter(is_draft=False)
    
    context = {
        'profile': profile,
        'posts': posts,
        'categories': categories,
        'selected_category': selected_category
    }
    return render(request, 'accounts/patient_dashboard.html', context)

@login_required
def blog_detail(request, blog_id):
    blog = get_object_or_404(BlogPost, id=blog_id, is_draft=False)
    context = {"blog": blog}
    return render(request, "accounts/blog_detail.html", context)