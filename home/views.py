import datetime
import re
from collections import defaultdict
from math import sqrt
# from PIL import Image
from PIL import Image

import home.utils as utils

import dateutil.parser
import facebook
import io
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render, redirect


from accounts.forms import InsertWord, validate_word, InsertPost
from .models import UserData, BannedWord, StatPerson, StatPost, Post


def index(request, page_number=0):
    user_data, token, graph, page_id = utils.get_graph_api_inf(request.user.id, page_number)

    data = graph.get_object(id=page_id, fields='name, picture')
    posts_data = graph.get_connections(id=page_id, connection_name='feed?limit=3')
    utils.pretty_print_json(posts_data)
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
        utils.like_comments_in_every_post( graph, page_id)

    # liking all comments in given post
    elif request.method == 'POST' and 'like_comments' in request.POST:
        utils.like_comments_in_post(request.POST.dict()['post_id_where_comments_to_like'], graph, page_id)

    # deleting comments in every post which including banned words from database
    elif request.method == 'POST' and 'delete_all_comments' in request.POST:
        utils.delete_comments_in_every_post(graph, user_data.pages[page_number].words, page_id)

    # deleting comments in given post which including banned words from database
    elif request.method == 'POST' and 'delete_comments' in request.POST:
        utils.delete_comments_in_post(request.POST.dict()['post_id_where_comments_to_delete'], graph, user_data.pages[page_number].words, page_id)

    # deleting given post
    elif request.method == 'POST' and 'delete_post' in request.POST:
        utils.delete_post(request.POST.dict()['post_to_delete'], graph)

    return render(request, 'home/index.html', context)


def start_page(request):
    return render(request, 'home/start.html')


def management_page(request, page_number=0):
    return render(request, 'home/management.html', {'page_number': page_number})


def banned_words_page(request, page_number=0):
    user_data = UserData.objects.get(user_id=request.user.id)
    banned_words = [banned_word.word for banned_word in user_data.pages[page_number].words]

    if request.method == 'POST' and 'add_word' in request.POST:
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
                return render(request, 'home/banned_words.html', {'page_number': page_number,
                                                                  'words': banned_words,
                                                                  'form': form,
                                                                  'isValid': True})
            else:
                form = InsertWord()
                return render(request, 'home/banned_words.html', {'page_number': page_number,
                                                                  'words': banned_words,
                                                                  'form': form,
                                                                  'isValid': False})
        else:
            form = InsertWord()
            return render(request, 'home/banned_words.html', {'page_number': page_number,
                                                              'words': banned_words,
                                                              'form': form,

                                                              'isValid': False})
    elif request.method == 'POST' and 'delete_word' in request.POST:
        word_id = request.POST.dict()['delete_word']
        word = user_data.pages[page_number].words[int(word_id)]
        # TODO works only for first word on the list
        user_data.pages[page_number].words.remove(word)
        user_data.save()
        form = InsertWord()

    else:
        form = InsertWord()

    return render(request, 'home/banned_words.html', {'page_number': page_number,
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


def statistics(request, page_number=0):
    return render(request, 'home/statistics/statistics.html', {'page_number': page_number})


def top_commenters(request, page_number=0):
    user_data, token, graph, page_id = utils.get_graph_api_inf(request.user.id, page_number)

    user_data = UserData.objects.get(user_id=request.user.id)
    context = {'page_number': page_number}

    if request.method == 'POST' and 'refresh_data' in request.POST:
        utils.refresh_top_commenters(graph, page_id, request.user.id, page_number)

    context['top_5_commenters'] = user_data.pages[page_number].statistics.top_commenters
    context['commenters_last_refresh'] = user_data.pages[page_number].statistics.top_commenters_refresh_date

    return render(request, 'home/statistics/top_commenters.html', context)


def add_post(request, page_number=0):
    if request.method == 'POST':
        form = InsertPost(request.POST, request.FILES)
        print(request.FILES)
        if form.is_valid():
            message = form.cleaned_data['message']
            image = form.cleaned_data.get('image')
            date = form.cleaned_data['date']

            user_data, token, graph, page_id = utils.get_graph_api_inf(request.user.id, page_number)
            if image is None:
                if utils.datetime_to_string() > date:
                    graph.put_object(parent_object='me', message=message, page_number=page_id, connection_name='feed')
                else:
                    # TODO add to scheduler
                    post = Post(message=message, image=None, scheduled_date=date, image_bytes=None)
                    user_data.pages[page_number].posts.append(post)
                    user_data.save()
            else:
                img = Image.open(image, mode='r')
                img_byte_array = io.BytesIO()
                img.save(img_byte_array, format=img.format)
                img_byte_array = img_byte_array.getvalue()

                if utils.datetime_to_string() > date:
                    graph.put_photo(image=img_byte_array, message=message)
                else:
                    # TODO add to scheduler
                    post = Post(message=message, image=image, scheduled_date=date, image_bytes=img_byte_array)
                    user_data.pages[page_number].posts.append(post)
                    user_data.save()

        return render(request, 'home/add_post.html', {'page_number': page_number,
                                                      'form': InsertPost(),
                                                      'isValid': True})
    else:
        return render(request, 'home/add_post.html', {'page_number': page_number,
                                                      'form': InsertPost(),
                                                      'isValid': False})


def top_shared_posts(request, page_number=0):
    user_data, token, graph, page_id = utils.get_graph_api_inf(request.user.id, page_number)
    user_data = UserData.objects.get(user_id=request.user.id)
    context = {'page_number': page_number}

    if request.method == 'POST' and 'refresh_data' in request.POST:
        utils.refresh_top_shared(graph, page_id, request.user.id, page_number)

    context['top_5_posts'] = user_data.pages[page_number].statistics.top_shared_posts
    context['last_refresh'] = user_data.pages[page_number].statistics.top_shared_posts_refresh_date
    context['post_data'] = utils.get_post_data(graph, context['top_5_posts'])

    return render(request, 'home/statistics/top_x_posts.html', context)


def top_commented_posts(request, page_number=0):
    user_data, token, graph, page_id = utils.get_graph_api_inf(request.user.id, page_number)
    user_data = UserData.objects.get(user_id=request.user.id)
    context = {'page_number': page_number}

    if request.method == 'POST' and 'refresh_data' in request.POST:
        utils.refresh_top_commented(graph, page_id, request.user.id, page_number)
        # redirect('Top 5 commented posts')
        redirect('home/statistics/top_x_posts.html')

    context['top_5_posts'] = user_data.pages[page_number].statistics.top_commented_posts
    context['last_refresh'] = user_data.pages[page_number].statistics.top_commented_posts_refresh_date
    context['post_data'] = utils.get_post_data(graph, context['top_5_posts'])

    return render(request, 'home/statistics/top_x_posts.html', context)


def top_liked_posts(request, page_number=0):
    user_data, token, graph, page_id = utils.get_graph_api_inf(request.user.id, page_number)
    user_data = UserData.objects.get(user_id=request.user.id)
    context = {'page_number': page_number}

    if request.method == 'POST' and 'refresh_data' in request.POST:
        utils.refresh_top_likes(graph, page_id, request.user.id, page_number)

    context['top_5_posts'] = user_data.pages[page_number].statistics.top_liked_posts
    context['last_refresh'] = user_data.pages[page_number].statistics.top_liked_posts_refresh_date
    context['post_data'] = utils.get_post_data(graph, context['top_5_posts'])

    return render(request, 'home/statistics/top_x_posts.html', context)
