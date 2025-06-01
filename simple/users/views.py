from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from functools import wraps
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q


def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            profile = getattr(request.user, 'profile', None)
            if profile and profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                # redirect or return permission denied
                return redirect('permission_denied')  # create this view or change
        return _wrapped_view
    return decorator

def permission_denied_view(request):
    return render(request, 'users/permission_denied.html', status=403)


@role_required(['admin', 'manager'])
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            role = form.cleaned_data['role']
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()

            return redirect('user_list')  # Replace with your actual success URL
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile_view(request):
    profile = request.user.profile
    return render(request, 'users/profile.html', {'profile': profile})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('profile')  # or any page after login
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


def user_list_view(request):
    query = request.GET.get('q', '').strip()
    role = request.GET.get('role', '').strip()
    users = User.objects.all()

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(profile__role__icontains=query)
        )

    if role:
        users = users.filter(profile__role=role)

    return render(request, 'users/user_list.html', {
        'users': users,
        'query': query,
        'role': role,
    })



@role_required(['admin', 'manager'])
def edit_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = getattr(user, 'profile', None)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            if profile:
                profile.role = form.cleaned_data['role']
                profile.save()

            messages.success(request, 'User updated successfully.')
            return redirect('user_list')
    else:
        form = CustomUserCreationForm(instance=user, initial={
            'role': profile.role if profile else ''
        })

    return render(request, 'users/edit_user.html', {'form': form, 'user': user})


@role_required(['admin', 'manager'])
def delete_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('user_list')

    return render(request, 'users/confirm_delete.html', {'user': user})
