
from django.shortcuts import render, redirect
from django.contrib.auth import login

from home.models import UserData, Page, Statistics
from .forms import SignUpForm, InsertToken, validate_token_page_id


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_data = UserData(user=user, pages=[])
            user_data.save()
            login(request, user)
            return redirect('add_page')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def get_token(request):
    if request.method == 'POST':
        form = InsertToken(request.POST)

        if form.is_valid():
            token = form.cleaned_data['token']
            page_id = form.cleaned_data['page_id']
            if validate_token_page_id(token, page_id):
                current_user = request.user
                user_data = UserData.objects.get(user_id=current_user.id)
                page = Page(
                    page_id=page_id,
                    token=token,
                    words=[],
                    statistics=Statistics(
                        top_commenters=[],
                        top_liked_posts=[],
                        top_commented_posts=[],
                        top_shared_posts=[])
                )
                user_data.pages.append(page)
                user_data.save()
                return redirect('home')
            else:
                return render(request, 'accounts/add_page.html', {'form': form, 'isValid': False})
        else:
            return render(request, 'accounts/add_page.html', {'form': form, 'isValid': False})
    else:
        form = InsertToken()

    return render(request, 'accounts/add_page.html', {'form': form, 'isValid': True})
