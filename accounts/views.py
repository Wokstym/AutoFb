from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login

from home.models import UserData, BannedWord, Page
from .forms import SignUpForm, InsertToken, validate_token_page_id


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            userData = UserData(user=user, pages=[])
            userData.save()
            login(request, user)
            return redirect('add_page')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def get_token(request):
    if request.method == 'POST':
        form = InsertToken(request.POST)
        token = form.cleaned_data['token']
        page_id = form.cleaned_data['page_id']

        if form.is_valid() and validate_token_page_id(token, page_id):

            current_user = request.user
            userData = UserData.objects.get(user_id=current_user.id)

            page = Page(page_id=page_id, token=token, words=[])
            userData.pages.append(page)
            userData.save()

            return redirect('home')
        else:
            return render(request, 'accounts/add_page.html', {'form': form, 'isValid': False})
    else:
        form = InsertToken()

    return render(request, 'accounts/add_page.html', {'form': form, 'isValid': True})
