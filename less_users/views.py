from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views import View

from less_users.forms import UserRegisterForm, UserUpdateForm


class HomeView(View):
    def get(self, request):
        return render(request, 'less_users/home.html')


class RegisterView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'less_users/register.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account >>{username}<< has been created! You can log in now.')
        return redirect('home')


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        u_form = UserUpdateForm(instance=request.user)
        return render(request, 'less_users/profile.html', {'u_form': u_form})

    def post(self, request):
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
        return render(request, 'less_users/profile.html', {'u_form': u_form})