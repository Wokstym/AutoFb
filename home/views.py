import datetime
import re
from collections import defaultdict

from dateutil.tz import UTC
from django.utils import timezone

import home.utils as utils

import dateutil.parser
import facebook
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render

from accounts.forms import InsertWord, validate_word, InsertPost
from .models import UserData, BannedWord, StatPerson


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
        utils.like_comments_in_every_post(posts, graph, page_id)

    # liking all comments in given post
    elif request.method == 'POST' and 'like_comments' in request.POST:
        utils.like_comments_in_post(request.POST.dict(), graph, page_id)

    # deleting comments in every post which including banned words from database
    elif request.method == 'POST' and 'delete_all_comments' in request.POST:
        utils.delete_comments_in_every_post(posts, graph, user_data.pages[page_number].words, page_id)

    # deleting comments in given post which including banned words from database
    elif request.method == 'POST' and 'delete_comments' in request.POST:
        utils.delete_comments_in_post(request.POST.dict(), graph, user_data.pages[page_number].words, page_id)

    # deleting given post
    elif request.method == 'POST' and 'delete_post' in request.POST:
        utils.delete_post(request.POST.dict(), graph)

    return render(request, 'home/index.html', context)


def start_page(request):
    return render(request, 'home/start.html')


def management_page(request, page_number=0):
    return render(request, 'home/management.html', {'page_number': page_number})


def banned_words_page(request, page_number=0):
    user_data = UserData.objects.get(user_id=request.user.id)
    banned_words = [banned_word.word for banned_word in user_data.pages[page_number].words]

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


def statistics_page(request, page_number=0):
    user_data, token, graph, page_id = utils.get_graph_api_inf(request.user.id, page_number)

    user_data = UserData.objects.get(user_id=request.user.id)

    if request.method == 'POST' and 'refresh_data' in request.POST:
        #
        # posts_data = graph.get_connections(id=page_id, connection_name='feed?&limit=50&summary=1')
        # user_id_to_post_nr = defaultdict(lambda: 0)
        #
        # while posts_data['data']:
        #     posts_id = [dictionary_with_comments['id'] for dictionary_with_comments in posts_data['data']]
        #
        #     list_of_posts_with_comments = graph.get_objects(ids=posts_id, fields='comments')
        #     # utils.pretty_print_json( list_of_posts_with_comments)
        #     comments_data = [comments_dict for comments_dict in
        #                      [comments_in_posts[1] for comments_in_posts in list_of_posts_with_comments.items()] if
        #                      'comments' in comments_dict]
        #
        #     list_of_commenters_id = []
        #     for comments_in_one_post in comments_data:
        #         cursor_comments_data = comments_in_one_post['comments']
        #         post_id = comments_in_one_post['id']
        #
        #         while cursor_comments_data['data']:
        #             # print(len(cursor_comments_data['data']))
        #             list_of_commenters_id += [comment['from']['id'] for comment in cursor_comments_data['data'] if
        #                                       comment['from']['id'] != page_id]
        #
        #             if len(cursor_comments_data['data']) < 25:
        #                 break
        #             cursor_comments_data = graph.get_connections(
        #                 id=post_id,
        #                 connection_name='comments?&after=' + cursor_comments_data['paging']['cursors']['after']
        #             )
        #
        #     for comment_id in list_of_commenters_id:
        #         user_id_to_post_nr[comment_id] += 1
        #     posts_data = graph.get_connections(
        #         id=page_id,
        #         connection_name='feed?&limit=50&after=' + posts_data['paging']['cursors']['after']
        #     )
        #
        # top_5_users = []
        # for i, (user_id, nr_of_comments) in enumerate(
        #         sorted(user_id_to_post_nr.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:5]):
        #     user_name_photo = graph.get_object(id=user_id, fields='picture, name')
        #     stat_person = StatPerson(
        #         position=(i + 1),
        #         name=user_name_photo['name'],
        #         photo_url=user_name_photo['picture']['data']['url'],
        #         comments_nr=nr_of_comments
        #     )
        #
        #     top_5_users.append(stat_person)
        # user_data.pages[page_number].statistics.top_commenters = top_5_users
        # TODO cos jest jebniete z tymi datami
        user_data.pages[page_number].statistics.top_commenters_refresh_date = timezone.now()
        user_data.save()

    top_5_users = user_data.pages[page_number].statistics.top_commenters
    last_refresh = user_data.pages[page_number].statistics.top_commenters_refresh_date

    return render(request, 'home/statistics.html',
                  {'page_number': page_number, 'top_5_users': top_5_users, 'last_refresh': last_refresh})


def add_post(request, page_number=0):
    if request.method == 'POST':
        form = InsertPost(request.POST, request.FILES)
        if form.is_valid():
            message = form.cleaned_data['message']
            image = form.cleaned_data['image']
            _, _, graph, page_id = utils.get_graph_api_inf(request.user.id, page_number)
            if image is None:
                graph.put_object(parent_object='me', message=message, page_number=page_id, connection_name='feed')
            else:
                print("adding image")
                # doesn't work yet
                # graph.put_photo(image=open('image', 'rb'), message=message)

        return render(request, 'home/add_post.html', {'page_number': page_number,
                                                      'form': InsertPost(),
                                                      'isValid': True})
    else:
        return render(request, 'home/add_post.html', {'page_number': page_number,
                                                      'form': InsertPost(),
                                                      'isValid': False})
