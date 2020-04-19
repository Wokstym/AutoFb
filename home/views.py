from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
import facebook

from accounts.forms import SignUpForm
from .models import UserData


def index(request):
    current_user = request.user
    userData= UserData.objects.get(user_id=current_user.id)
    token = userData.token
    graph = facebook.GraphAPI(token)
    # page_id = userData.pages.page_id
    page_id = '110540857220080'
    default_info = graph.get_object(id=page_id, fields='posts')
    posts = default_info['posts']['data']
    return render(request, 'home/index.html', {'posts': posts})
    # return render(request, 'home/index.html')

def start_page(request):
    return render(request, 'home/start.html')

