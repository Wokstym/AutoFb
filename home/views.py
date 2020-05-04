from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
import facebook
from django.core.paginator import Paginator
import json
import re

from accounts.forms import SignUpForm, InsertWord, validate_word

from .models import UserData, Page, BannedWord


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
        'page_number': page_number,
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

    # deleting comments in every post which including banned words from database
    elif request.method == 'POST' and 'delete_all_comments' in request.POST:
        delete_comments_in_every_post(posts, graph, userData.pages[page_number].words)

    # deleting comments in given post which including banned words from database
    elif request.method == 'POST' and 'delete_comments' in request.POST:
        delete_comments_in_post(request.POST.dict(), graph, userData.pages[page_number].words)

    # deleting given post
    elif request.method == 'POST' and 'delete_post' in request.POST:
        delete_post(request.POST.dict(), graph)

    return render(request, 'home/index.html', context)


def like_comments_in_every_post(posts, graph):
    for post in posts:
        if post['comments'] is not None:
            for comment in post['comments']:
                graph.put_like(object_id=comment['id'])


def split(comments):
    comments = comments.replace("[", "")
    comments = comments.replace("]", "")
    comments = comments.replace("'", "\"")
    return comments.split('}, ')


def comment_to_json(comment):
    comment = comment.replace("}", "")
    comment = "{" + comment + "}"
    return json.loads(comment)


def like_comments_in_post(data_dict, graph):
    split_comments = split(data_dict['comments_to_like'])

    for i, comment in enumerate(split_comments):
        if i % 2 != 0:
            comment_json = comment_to_json(comment)
            print(comment_json["id"])
            graph.put_like(object_id=comment_json["id"])


def split_words(words):
    words = re.sub(r'[0-9]', '', words)
    words = re.sub(r'[^\w\s]', '', words)
    words = words.lower()
    return words.split(' ')


def delete_comments_in_every_post(posts, graph, banned_words):
    array_with_banned_words = []
    for banned_word in banned_words:
        array_with_banned_words.append(banned_word.word)

    for post in posts:
        if post['comments'] is not None:
            for comment in post['comments']:
                print(comment["message"])
                for word in split_words(comment["message"]):
                    print(word)
                    if word in array_with_banned_words:
                        graph.delete_object(comment["id"])
                        break


def delete_comments_in_post(data_dict, graph, banned_words):
    array_with_banned_words = []
    for banned_word in banned_words:
        array_with_banned_words.append(banned_word.word)

    print(array_with_banned_words)
    split_comments = split(data_dict['comments_to_delete'])
    for i, comment in enumerate(split_comments):
        if i % 2 != 0:
            comment_json = comment_to_json(comment)
            print(comment_json["message"])

            for word in split_words(comment_json["message"]):
                print(word)
                if word in array_with_banned_words:
                    graph.delete_object(comment_json["id"])
                    break


def delete_post(data_dict, graph):
    post_id = data_dict['post_to_delete']
    print(post_id)
    graph.delete_object(id=post_id)


def start_page(request):
    return render(request, 'home/start.html')


def management_page(request, page_number=0):
    if request.method == 'POST':
        form = InsertWord(request.POST)

        if form.is_valid():
            word = form.cleaned_data['word']
            if validate_word(word):
                word = re.sub(r'[0-9]', '', word)
                word = re.sub(r'[^\w\s]', '', word)
                word = word.lower()

                current_user = request.user
                userData = UserData.objects.get(user_id=current_user.id)

                banned_words = []
                for banned_word in userData.pages[page_number].words:
                    banned_words.append(banned_word.word)

                if word not in banned_words:
                    banned_word = BannedWord(word=word)
                    userData.pages[page_number].words.append(banned_word)
                    userData.save()
                form = InsertWord()
                return render(request, 'home/management.html', {'form': form, 'isValid': True})
            else:
                form = InsertWord()
                return render(request, 'home/management.html', {'form': form, 'isValid': False})
        else:
            form = InsertWord()
            return render(request, 'home/management.html', {'form': form, 'isValid': False})
    else:
        form = InsertWord()

    return render(request, 'home/management.html', {'form': form, 'isValid': True})
