from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
import facebook
from django.core.paginator import Paginator

from accounts.forms import SignUpForm

from .models import UserData

# zakomentowalem to, bo model sie zmienil wiec to by errory wyjebywalo, ale kurwa te jebane modele pierdolone
def index(request):
    current_user = request.user
    userData = UserData.objects.get(user_id=current_user.id)
    print(userData)
    # token = userData.token
    # graph = facebook.GraphAPI(token)
    #
    # # page_id = userData.pages.page_id
    # page_id = '110540857220080'
    # default_info = graph.get_object(id=page_id, fields='posts')
    # info = graph.get_object(page_id + "/picture?redirect=0")
    #
    # posts = default_info['posts']['data']
    # profile_image = info['data']['url']
    #
    # #print(posts)
    # # print(photo)
    #
    # for post in posts:
    #     #print(post['id'])
    #     #print(post)
    #     photo = graph.get_object(post['id'] + "?fields=object_id")
    #     if photo.get('object_id'):
    #         photo = graph.get_object(photo['object_id'] + "/picture")
    #         photo = photo['url']
    #         post['url'] = photo
    #         #print(post)
    #     else:
    #         post['url'] = None
    #
    # template = loader.get_template('home/index.html')
    # context = {
    #     'posts': posts,
    #     'image_url': profile_image,
    # }
    # paginator = Paginator(context['posts'], 3)
    # page = request.GET.get('page')
    # context['posts'] = paginator.get_page(page)
    #
    # # return HttpResponse(template.render(context, request))
    context = {
    #     'posts': posts,
    #     'image_url': profile_image,
     }
    return render(request, 'home/index.html', context)
    # return render(request, 'home/index.html')


def start_page(request):
    return render(request, 'home/start.html')
