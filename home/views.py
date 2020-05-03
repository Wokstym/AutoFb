from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
import facebook
from django.core.paginator import Paginator
import json

from accounts.forms import SignUpForm

from .models import UserData, Page


def index(request, page_number=0):
    current_user = request.user
    userData = UserData.objects.get(user_id=current_user.id)

    try:
        userData.pages[page_number]
    except:
        page_number = 0

    token = userData.pages[page_number].token
    graph = facebook.GraphAPI(token)
    page_id = userData.pages[page_number].page_id

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

    context = {
        'posts': posts,
        'image_url': profile_image,
    }
    paginator = Paginator(context['posts'], 3)
    page = request.GET.get('page')
    context['posts'] = paginator.get_page(page)

    # liking all comments in every post
    if request.method == 'POST' and 'like_all_comments' in request.POST:
        like_comments_in_every_post(posts, graph)

    # liking all comments in given post
    elif request.method == 'POST' and 'like_comments' in request.POST:
        like_comments_in_post(request.POST.dict(), graph)

    # deleting given post
    elif request.method == 'POST' and 'delete_post' in request.POST:
        delete_post(request.POST.dict(), graph)

    # return HttpResponse(template.render(context, request))
    return render(request, 'home/index.html', context)


def like_comments_in_every_post(posts, graph):
    for post in posts:
        if post['comments'] is not None:
            for comment in post['comments']:
                graph.put_like(object_id=comment['id'])


def like_comments_in_post(data_dict, graph):
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


def delete_post(data_dict, graph):
    post_id = data_dict['post_to_delete']
    print(post_id)
    graph.delete_object(id=post_id)


def start_page(request):
    return render(request, 'home/start.html')


def management_page(request):
    return render(request, 'home/management.html')
