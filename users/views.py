from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from allauth.account.utils import send_email_confirmation
from django.contrib.auth.models import User
from .forms import *


def profile_view(request, username=None):
    if username:
        profile = get_object_or_404(User, username=username).profile
    else:
        try:
            profile = request.user.profile
        except:
            return redirect('account_login')
    return render(request, 'users/profile.html', {'profile': profile})


@login_required
def profile_edit_view(request):
    form = ProfileForm(instance=request.user.profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')

    if request.path == reverse('profile_onboarding'):
        onboarding = True
    else:
        onboarding = False

    return render(request, 'users/profile_edit.html', {'form': form, 'onboarding': onboarding})


@login_required
def profile_settings_view(request):
    return render(request, 'users/profile_settings.html')


@login_required
def profile_email_change(request):
    if request.htmx:
        form = EmailForm(instance=request.user)

        return render(request, 'partials/email_form.html', {'form': form})

    if request.method == 'POST':
        form = EmailForm(request.POST, instance=request.user)

        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if email is already use
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.warning(request, f'{email} is already in use.')

                return redirect('profile_settings')

            form.save()

            # Then Signal updates email address and set verified to False

            # Then send confirmation email
            send_email_confirmation(request, request.user)

            return redirect('profile_settings')

        else:
            messages.warning(request, 'Form is invalid.')
            return redirect('profile_settings')

    return redirect('home')


@login_required
def profile_email_verify(request):
    send_email_confirmation(request, request.user)
    return redirect('profile_settings')


@login_required
def profile_delete_view(request):
    user = request.user

    if request.method == 'POST':
        logout(request)
        user.delete()
        messages.success(request, 'Account has been deleted.')
        return redirect('home')

    return render(request, 'users/profile_delete.html')

