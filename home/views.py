from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
import facebook

from .models import UserData


def index(request):
    userData= UserData.objects.get(user_id=3) # narazie biorę testusera po id, dopoki nie mamy logowania
    token = userData.token
    graph = facebook.GraphAPI(token)
    default_info = graph.get_object(id='110540857220080', fields='posts')
    posts = default_info['posts']['data']

    template = loader.get_template('home/index.html')
    context = {
        'posts': posts,
    }
    return HttpResponse(template.render(context, request))
