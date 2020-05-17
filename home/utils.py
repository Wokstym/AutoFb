import json
import re
from collections import defaultdict
from datetime import datetime

import dateutil
import facebook
from django.http import Http404

from home.models import UserData, StatPerson, StatPost


def split_words(words):
    words = re.sub(r'[0-9]', '', words)
    words = re.sub(r'[^\w\s]', '', words)
    words = words.lower()
    return words.split(' ')


def pretty_print_json(json_string):
    print(json.dumps(json_string, indent=4))


def like_comments_in_every_post(graph, page_id):
    posts = graph.get_all_connections(id=page_id, connection_name='feed?&limit=50&fields=comments')
    for post in posts:
        if 'comments' in post:
            like_comments_in_post(post['id'], graph, page_id)


def like_comments_in_post(post_id, graph, page_id):
    comments = graph.get_all_connections(id=post_id, connection_name='comments?&summary=total_count&limit=10000000000')

    for comment in comments:
        if comment["from"]["id"] != page_id:
            graph.put_like(object_id=comment["id"])


def delete_comments_in_every_post(graph, banned_words, page_id):
    posts = graph.get_all_connections(id=page_id, connection_name='feed?&limit=50&fields=comments')

    for post in posts:
        if 'comments' in post:
            delete_comments_in_post(post['id'], graph, banned_words, page_id)


def delete_comments_in_post(post_id, graph, banned_words, page_id):
    array_with_banned_words = [word.word for word in banned_words if word.word is not None]
    comments = graph.get_all_connections(id=post_id, connection_name='comments?&summary=total_count&limit=10000000000')

    for comment in comments:
        if comment["from"]["id"] != page_id:
            print("messsage= " + comment["message"])
            for word in split_words(comment["message"]):
                print("\tword= " + word)
                if word in array_with_banned_words:
                    graph.delete_object(comment["id"])
                    break


def delete_post(post_id, graph):
    graph.delete_object(id=post_id)


def get_graph_api_inf(user_id, page_number):
    user_data = UserData.objects.get(user_id=user_id)

    if len(user_data.pages) <= page_number:
        raise Http404("Fanpage data not found")

    token = user_data.pages[page_number].token
    graph = facebook.GraphAPI(token)
    page_id = user_data.pages[page_number].page_id

    return user_data, token, graph, page_id


def datetime_to_string():
    return datetime.now().strftime("%d/%m/%Y, %H:%M")


def string_to_datetime(date_str):
    return datetime.strptime(date_str, "%d/%m/%Y, %H:%M")


def get_post_data(graph, top_5_posts):
    context_post_data = []
    if top_5_posts is None:
        return context_post_data
    for post in top_5_posts:
        post_data = graph.get_connections(
            id=post.post_id,
            connection_name='?&fields=reactions.limit(0).summary(total_count),shares,comments.limit(0).summary('
                            'total_count), object_id, type, created_time, message '
        )
        if 'shares' in post_data:
            shares_nr = post_data['shares']['count']
        else:
            shares_nr = 0
        if 'reactions' in post_data:
            reactions_nr = post_data['reactions']['summary']['total_count']
        else:
            reactions_nr = 0
        if 'comments' in post_data:
            comments_nr = post_data['comments']['summary']['total_count']
        else:
            comments_nr = 0

        context_post = {'position': post.position,
                        'reactions_nr': reactions_nr,
                        'shares_nr': shares_nr,
                        'comments_nr': comments_nr,
                        'created_time': dateutil.parser.parse(post_data['created_time'])}

        if 'message' in post_data:
            context_post['message'] = post_data['message']

        if post_data['type'] == "photo":
            photo_data = graph.get_object(id=post_data['object_id'], fields='images')
            context_post['photo_source'] = photo_data['images'][0]['source']

        elif post_data['type'] == "video":
            video = graph.get_object(id=post_data['object_id'], fields='source')
            context_post['video_source'] = video['source']

        context_post_data.append(context_post)
    return context_post_data


def refresh_top_commenters(graph, page_id, user_id, page_number):
    user_data = UserData.objects.get(user_id=user_id)
    posts_data = graph.get_connections(id=page_id, connection_name='feed?&limit=50&summary=1')
    user_id_to_post_nr = defaultdict(lambda: 0)

    while posts_data['data']:
        posts_id = [dictionary_with_comments['id'] for dictionary_with_comments in posts_data['data']]

        list_of_posts_with_comments = graph.get_objects(ids=posts_id, fields='comments')
        comments_data = [comments_dict for comments_dict in
                         [comments_in_posts[1] for comments_in_posts in list_of_posts_with_comments.items()] if
                         'comments' in comments_dict]

        list_of_commenters_id = []
        for comments_in_one_post in comments_data:
            cursor_comments_data = comments_in_one_post['comments']
            post_id = comments_in_one_post['id']

            while cursor_comments_data['data']:
                list_of_commenters_id += [comment['from']['id'] for comment in cursor_comments_data['data'] if
                                          comment['from']['id'] != page_id]

                if len(cursor_comments_data['data']) < 25:
                    break
                cursor_comments_data = graph.get_connections(
                    id=post_id,
                    connection_name='comments?&after=' + cursor_comments_data['paging']['cursors']['after']
                )

        for comment_id in list_of_commenters_id:
            user_id_to_post_nr[comment_id] += 1
        posts_data = graph.get_connections(
            id=page_id,
            connection_name='feed?&limit=50&after=' + posts_data['paging']['cursors']['after']
        )

    top_5_users = []
    for i, (user_id, nr_of_comments) in enumerate(
            sorted(user_id_to_post_nr.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:5]):
        user_name_photo = graph.get_object(id=user_id, fields='picture, name')
        stat_person = StatPerson(
            position=(i + 1),
            name=user_name_photo['name'],
            photo_url=user_name_photo['picture']['data']['url'],
            comments_nr=nr_of_comments
        )

        top_5_users.append(stat_person)
    user_data.pages[page_number].statistics.top_commenters = top_5_users

    user_data.pages[page_number].statistics.top_commenters_refresh_date = datetime_to_string()
    user_data.save()


# ================================== Refreshing functions ================================== #

def refresh_top_shared(graph, page_id, user_id, page_number):
    user_data = UserData.objects.get(user_id=user_id)
    posts_data = graph.get_all_connections(id=page_id, connection_name='feed?&limit=50&fields=shares')

    post_id_to_react_nr = {}

    for post in posts_data:
        if 'shares' in post:
            post_id = post['id']
            share_nr = post['shares']['count']
            post_id_to_react_nr[post_id] = share_nr

    top_5_posts = []
    for i, (post_id, shares_nr) in enumerate(
            sorted(post_id_to_react_nr.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:5]):
        stat_post = StatPost(
            position=(i + 1),
            post_id=post_id,
            shares_nr=shares_nr
        )
        top_5_posts.append(stat_post)

    user_data.pages[page_number].statistics.top_shared_posts = top_5_posts
    user_data.pages[page_number].statistics.top_shared_posts_refresh_date = datetime_to_string()
    user_data.save()


def refresh_top_commented(graph, page_id, user_id, page_number):
    user_data = UserData.objects.get(user_id=user_id)
    posts_data = graph.get_all_connections(id=page_id, connection_name='feed?&limit=50&fields=comments.limit('
                                                                       '0).summary(total_count)')

    post_id_to_comment_nr = {}

    for post in posts_data:
        if 'comments' in post:
            post_id = post['id']
            comment_nr = post['comments']['summary']['total_count']
            post_id_to_comment_nr[post_id] = comment_nr

    top_5_posts = []
    for i, (post_id, comments_nr) in enumerate(
            sorted(post_id_to_comment_nr.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:5]):
        stat_post = StatPost(
            position=(i + 1),
            post_id=post_id,
            comments_nr=comments_nr
        )
        top_5_posts.append(stat_post)

    user_data.pages[page_number].statistics.top_commented_posts = top_5_posts
    user_data.pages[page_number].statistics.top_commented_posts_refresh_date = datetime_to_string()
    user_data.save()


def refresh_top_likes(graph, page_id, user_id, page_number):
    user_data = UserData.objects.get(user_id=user_id)
    posts_data = graph.get_all_connections(id=page_id, connection_name='feed?&limit=50&fields=reactions.limit('
                                                                       '0).summary(total_count)')

    post_id_to_react_nr = {}

    for post in posts_data:
        post_id = post['id']
        react_nr = post['reactions']['summary']['total_count']
        post_id_to_react_nr[post_id] = react_nr

    top_5_posts = []
    for i, (post_id, react_nr) in enumerate(
            sorted(post_id_to_react_nr.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:5]):
        stat_post = StatPost(
            position=(i + 1),
            post_id=post_id,
            reactions_nr=react_nr
        )
        top_5_posts.append(stat_post)

    user_data.pages[page_number].statistics.top_liked_posts = top_5_posts
    user_data.pages[page_number].statistics.top_liked_posts_refresh_date = datetime_to_string()
    user_data.save()
