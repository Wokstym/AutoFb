import json
import re


def split(comments):
    comments = comments.replace("[", "")
    comments = comments.replace("]", "")
    comments = comments.replace("'", "\"")
    return comments.split('}, ')


def comment_to_json(comment):
    comment = comment.replace("}", "")
    comment = "{" + comment + "}"
    return json.loads(comment)


def split_words(words):
    words = re.sub(r'[0-9]', '', words)
    words = re.sub(r'[^\w\s]', '', words)
    words = words.lower()
    return words.split(' ')


def pretty_print_json(json_string):
    print(json.dumps(json_string, indent=4))


def like_comments_in_every_post(posts, graph):
    for post in posts:
        if 'comments' in post:
            for comment in post['comments']:
                graph.put_like(object_id=comment['id'])


def like_comments_in_post(data_dict, graph):
    split_comments = split(data_dict['comments_to_like'])
    print(data_dict['comments_to_like'])
    for i, comment in enumerate(split_comments):
        if i % 2 != 0:
            comment_json = comment_to_json(comment)
            graph.put_like(object_id=comment_json["id"])


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


