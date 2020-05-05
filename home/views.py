import json
import re
from collections import defaultdict
from datetime import datetime

import dateutil.parser
import facebook
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render

from accounts.forms import InsertWord, validate_word
from .models import UserData, BannedWord


def index(request, page_number=0):
    current_user = request.user
    userData = UserData.objects.get(user_id=current_user.id)

    if len(userData.pages) <= page_number:
        raise Http404("Fanpage data not found")

    token = userData.pages[page_number].token
    graph = facebook.GraphAPI(token)
    page_id = userData.pages[page_number].page_id

    info = graph.get_object(page_id + "/picture?redirect=0")
    profile_image = info['data']['url']
    fanpage_name = graph.get_object(id=page_id, fields='name')['name']

    posts = get_posts(graph, page_id)

    for post in posts:
        photo = graph.get_object(post['id'] + "?fields=object_id")
        comments = graph.get_connections(id=post['id'], connection_name='comments')['data']
        post['created_time'] = dateutil.parser.parse(post['created_time'])

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
        'name': fanpage_name
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
                return render(request, 'home/management.html', {'page_number': page_number,
                                                                'form': form,
                                                                'isValid': True})
            else:
                form = InsertWord()
                return render(request, 'home/management.html', {'page_number': page_number,
                                                                'form': form,
                                                                'isValid': False})
        else:
            form = InsertWord()
            return render(request, 'home/management.html', {'page_number': page_number,
                                                            'form': form,
                                                            'isValid': False})
    else:
        form = InsertWord()

    return render(request, 'home/management.html', {'page_number': page_number,
                                                    'form': form,
                                                    'isValid': True})


def pages(request):
    current_user = request.user
    userData = UserData.objects.get(user_id=current_user.id)
    i = -1
    user_pages = []

    for _ in userData.pages:
        i += 1
        token = userData.pages[i].token
        graph = facebook.GraphAPI(token)
        page_id = userData.pages[i].page_id
        info = graph.get_object(page_id + "/picture?redirect=0")
        fanpage_name = graph.get_object(id=page_id, fields='name')['name']
        profile_image = info['data']['url']
        user_pages.append({
            'photo': profile_image,
            'name':fanpage_name
        })
    print(i)
    print(user_pages)

    return render(request, 'home/pages.html', {'pages': user_pages})


def statistics_page(request, page_number=0):
    userData = UserData.objects.get(user_id=request.user.id)
    token = userData.pages[page_number].token
    graph = facebook.GraphAPI(token)
    page_id = userData.pages[page_number].page_id

    user_id_to_post_nr = defaultdict(lambda: 0)
    for post in get_posts(graph, page_id):
        comments = graph.get_connections(id=post['id'], connection_name='comments')['data']

        for comment in comments:
            comment_user_id = comment['from']['id']
            user_id_to_post_nr[comment_user_id] += 1

    top_5_users = []
    for (user_id, nr_of_posts) in sorted(user_id_to_post_nr.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:5]:
        user_name_photo = graph.get_object(id=user_id, fields='picture, name')

        top_5_users.append({
            'name': user_name_photo['name'],
            'picture': user_name_photo['picture']['data']['url'],
            'nr_of_posts': nr_of_posts
        })

    return render(request, 'home/statistics.html', {'page_number': page_number, 'top_5_users': top_5_users})


def get_posts(graph, page_id):
    default_info = graph.get_object(id=page_id, fields='posts')
    return default_info['posts']['data']
