import json
import re
from collections import defaultdict

import dateutil.parser
import facebook
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render

from accounts.forms import InsertWord, validate_word
from .models import UserData, BannedWord


def index(request, page_number=0):
    user_data = UserData.objects.get(user_id=request.user.id)

    if len(user_data.pages) <= page_number:
        raise Http404("Fanpage data not found")

    token = user_data.pages[page_number].token
    graph = facebook.GraphAPI(token)
    page_id = user_data.pages[page_number].page_id

    data = graph.get_object(id=page_id, fields='name, picture, posts')
    posts_data = graph.get_connections(id=page_id, connection_name='feed?limit=20')
    # pretty_print_json(comments_test)
    # pretty_print_json(data)

    profile_image_url = data['picture']['data']['url']
    page_name = data['name']
    # posts = data['posts']['data']

    posts = posts_data['data']

    for post in posts:
        post_data = graph.get_object(id=post['id'], fields='comments, object_id, type')

        post['created_time'] = dateutil.parser.parse(post['created_time'])

        if post_data['type'] == "photo":
            photo_data = graph.get_object(id=post_data['object_id'], fields='images')
            post['photo_source'] = photo_data['images'][0]['source']

        elif post_data['type'] == "video":
            video = graph.get_object(id=post_data['object_id'], fields='source')
            post['video_source'] = video['source']

        if 'comments' in post_data:
            post['comments'] = post_data['comments']['data']



    context = {
        'page_number': page_number,
        'posts': posts,
        'image_url': profile_image_url,
        'name': page_name
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
        delete_comments_in_every_post(posts, graph, user_data.pages[page_number].words)

    # deleting comments in given post which including banned words from database
    elif request.method == 'POST' and 'delete_comments' in request.POST:
        delete_comments_in_post(request.POST.dict(), graph, user_data.pages[page_number].words)

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
    user_data = UserData.objects.get(user_id=request.user.id)

    banned_words = []
    for banned_word in user_data.pages[page_number].words:
        banned_words.append(banned_word.word)
    if request.method == 'POST':
        form = InsertWord(request.POST)

        if form.is_valid():
            word = form.cleaned_data['word']
            if validate_word(word):
                word = re.sub(r'[0-9]', '', word)
                word = re.sub(r'[^\w\s]', '', word)
                word = word.lower()

                if word not in banned_words:
                    banned_word = BannedWord(word=word)
                    user_data.pages[page_number].words.append(banned_word)
                    user_data.save()
                form = InsertWord()
                return render(request, 'home/management.html', {'page_number': page_number,
                                                                'words': banned_words,
                                                                'form': form,
                                                                'isValid': True})
            else:
                form = InsertWord()
                return render(request, 'home/management.html', {'page_number': page_number,
                                                                'words': banned_words,
                                                                'form': form,
                                                                'isValid': False})
        else:
            form = InsertWord()
            return render(request, 'home/management.html', {'page_number': page_number,
                                                            'words': banned_words,
                                                            'form': form,
                                                            'isValid': False})
    else:
        form = InsertWord()

    return render(request, 'home/management.html', {'page_number': page_number,
                                                    'words': banned_words,
                                                    'form': form,
                                                    'isValid': True})


def pages(request):
    user_data = UserData.objects.get(user_id=request.user.id)
    user_pages = []

    for page_data in user_data.pages:
        token = page_data.token
        graph = facebook.GraphAPI(token)
        page_id = page_data.page_id

        data = graph.get_object(id=page_id, fields='name, picture, posts')

        page_profile_image_url = data['picture']['data']['url']
        page_name = data['name']

        user_pages.append({
            'photo': page_profile_image_url,
            'name': page_name
        })

    return render(request, 'home/pages.html', {'pages': user_pages})


def statistics_page(request, page_number=0):
    user_data = UserData.objects.get(user_id=request.user.id)
    token = user_data.pages[page_number].token
    graph = facebook.GraphAPI(token)
    page_id = user_data.pages[page_number].page_id

    user_id_to_post_nr = defaultdict(lambda: 0)
    posts = graph.get_object(id=page_id, fields='posts')['posts']['data']
    for post in posts:
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


def pretty_print_json(json_string):
    print(json.dumps(json_string, indent=4))
