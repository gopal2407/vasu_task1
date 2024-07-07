from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import render, redirect
from django import views
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from app_main.models import Organisation, User
from app_main.forms import OrganisationForm, UserRegistrationForm, UserLoginForm, UserForm
from django.contrib.auth.mixins import LoginRequiredMixin


def logout_view(request):
    logout(request)
    return redirect(reverse_lazy('login'))


class UserRegistrationView(views.View):

    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'app_main/user_reg.html', context={'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            orgs = Organisation.objects.filter(email=form.cleaned_data['email'].lower(), is_global=False)
            is_org_admin = orgs.exists()
            if not is_org_admin:
                orgs = Organisation.objects.filter(name__iexact='global', is_global=True)
                if not orgs.exists():
                    return render(request, 'app_main/user_reg.html', context={'form': form, 'error': 'Contact admin, Global org not found!'})

            org = orgs.first()

            pwd = data.pop('password')
            data.pop('confirm_password')
            try:
                user = User.objects.create(**data)
                user.set_password(pwd)
                user.is_org_admin = is_org_admin
                user.organization = org
                user.save()
                return redirect(reverse_lazy('login'))
            except Exception as e:
                return render(request, 'app_main/user_reg.html', context={'form': form, 'error': str(e)})

        else:
            return render(request, 'app_main/user_reg.html', context={'form': form})


class UserLoginView(views.View):

    def get(self, request):
        form = UserLoginForm()
        return render(request, 'app_main/login.html', context={'form': form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        user = authenticate(username=form.data.get('email'), password=form.data.get('password'))
        if user:
            login(request, user)
            return redirect(reverse_lazy('home'))
        else:
            return render(request, 'app_main/login.html', context={'form': form, 'error': 'Invalid credentials!'})


@login_required(login_url='')
def home_view(request):
    if request.user.is_superuser:
        return redirect(reverse_lazy('super-admin'))
    elif request.user.is_org_admin:
        return redirect(reverse_lazy('org-admin'))
    else:
        return redirect(reverse_lazy('end-user'))


@login_required(login_url='')
def super_admin_view(request):
    return render(request, 'app_main/user/super_user.html')


@login_required(login_url='')
def org_admin_view(request):
    return render(request, 'app_main/user/org_admin_home.html')


@login_required(login_url='')
def end_user_view(request):
    return render(request, 'app_main/user/end_user_home.html')


class OrganisationView(LoginRequiredMixin, views.View):

    def get(self, request):
        form = OrganisationForm()
        orgs = Organisation.objects.filter(~Q(name__iexact='global') & ~Q(is_global=False))
        context = {'organisations': orgs, 'form': form}
        return render(request, 'app_main/org/org_master', context=context)

    def post(self, request):
        form = OrganisationForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            try:
                _ = Organisation.objects.create(**form.cleaned_data)
                return redirect(reverse_lazy('orgnisations'))
            except Exception as e:
                context['error'] = str(e)
                return render(request, 'app_main/org/org_master', context=context)


class UserView(LoginRequiredMixin, views.View):

    def get(self, request):
        form = UserForm()
        return render(request, 'app_main/user/user_create.html', context={'form': form})

    def post(self, request):
        form = UserForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            try:
                user = form.save(commit=True)
                user.organization = request.user.organization
                user.save()
                return redirect(reverse_lazy('users'))
            except Exception as e:
                context['error'] = str(e)
        return render(request, 'app_main/user/user_create.html', context=context)


class UserMasterView(LoginRequiredMixin, generic.ListView):
    model = User
    context_object_name = 'users'
    template_name = 'app_main/user/user_master.html'

    def get_queryset(self):
        users = User.objects.filter(organization=self.request.user.organization, is_org_admin=False)
        return users
