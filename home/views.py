from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
import facebook
from django.core.paginator import Paginator
import json

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
    info = graph.get_object(page_id + "/picture?redirect=0")

    posts = default_info['posts']['data']
    profile_image = info['data']['url']

    for post in posts:
        photo = graph.get_object(post['id'] + "?fields=object_id")
        comments = graph.get_connections(id=post['id'], connection_name='comments')['data']

        if photo.get('object_id'):
            photo = graph.get_object(photo['object_id'] + "/picture")
            photo = photo['url']
            post['url'] = photo
        else:
            post['url'] = None

        if not comments:
            post['comments'] = None
        else:
            post['comments'] = comments

    template = loader.get_template('home/index.html')
    context = {
        'posts': posts,
        'image_url': profile_image,
    }
    paginator = Paginator(context['posts'], 3)
    page = request.GET.get('page')
    context['posts'] = paginator.get_page(page)

    # liking all comments in every post
    if request.method == 'POST' and 'like_all_comments' in request.POST:
        for post in posts:
            if post['comments'] is not None:
                for comment in post['comments']:
                    graph.put_like(object_id=comment['id'])

    # liking all comments in given post
    elif request.method == 'POST' and 'like_comments' in request.POST:
        data_dict = request.POST.dict()
        comments = data_dict['comments_to_like']

        comments = comments.replace("[", "")
        comments = comments.replace("]", "")
        comments = comments.replace("'", "\"")
        split_comments = comments.split('}, ')

        for i, comment in enumerate(split_comments):
            if i % 2 != 0:
                comment = comment.replace("}", "")
                comment = "{" + comment + "}"
                comment_json = json.loads(comment)
                print(comment_json["id"])
                graph.put_like(object_id=comment_json["id"])

    # deleting given post
    elif request.method == 'POST' and 'delete_post' in request.POST:
        data_dict = request.POST.dict()
        post_id = data_dict['post_to_delete']
        print(post_id)
        graph.delete_object(id=post_id)

    #return HttpResponse(template.render(context, request))
    return render(request, 'home/index.html', context)
    

def start_page(request):
    return render(request, 'home/start.html')


def management_page(request):
    return render(request, 'home/management.html')
