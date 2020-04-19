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
    info = graph.get_object("110540857220080/picture?redirect=0")

    posts = default_info['posts']['data']
    profile_image = info['data']['url']

    #print(posts)
    # print(photo)

    for post in posts:
        #print(post['id'])
        #print(post)
        photo = graph.get_object(post['id'] + "?fields=object_id")
        if photo.get('object_id'):
            photo = graph.get_object(photo['object_id'] + "/picture")
            photo = photo['url']
            post['url'] = photo
            #print(post)
        else:
            post['url'] = None

    template = loader.get_template('home/index.html')
    context = {
        'posts': posts,
        'image_url': profile_image,
    }
    return HttpResponse(template.render(context, request))
