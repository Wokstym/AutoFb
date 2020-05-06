import json
import re


def split_words(words):
    words = re.sub(r'[0-9]', '', words)
    words = re.sub(r'[^\w\s]', '', words)
    words = words.lower()
    return words.split(' ')


def pretty_print_json(json_string):
    print(json.dumps(json_string, indent=4))


def like_comments_in_every_post(posts, graph, page_id):
    for post in posts:
        if 'comments' in post:
            for comment in post['comments']:
                if comment["from"]["id"] != page_id:
                    graph.put_like(object_id=comment['id'])


def like_comments_in_post(data_dict, graph, page_id):
    split_comments = json.loads(data_dict['comments_to_like'].replace("'", '"'))
    pretty_print_json(split_comments)
    for comment in split_comments:
        if comment["from"]["id"] != page_id:
            graph.put_like(object_id=comment["id"])


def delete_comments_in_every_post(posts, graph, banned_words, page_id):
    array_with_banned_words = [banned_word.word for banned_word in banned_words]

    for post in posts:
        if 'comments' in post:
            delete_comments_from_json(post['comments'], graph, array_with_banned_words, page_id)


def delete_comments_in_post(data_dict, graph, banned_words, page_id):
    array_with_banned_words = [word.word for word in banned_words]
    fix_split_comments_json = json.loads(data_dict['comments_to_delete'].replace("'", '"'))
    delete_comments_from_json(fix_split_comments_json, graph, array_with_banned_words, page_id)


def delete_comments_from_json(comments, graph, banned_words_arr_str, page_id):
    for comment in comments:
        print("messsage= " + comment["message"])

        if comment["from"]["id"] != page_id:
            for word in split_words(comment["message"]):
                print("\tword= " + word)
                if word in banned_words_arr_str:
                    graph.delete_object(comment["id"])
                    break


def delete_post(data_dict, graph):
    post_id = data_dict['post_to_delete']
    print(post_id)
    graph.delete_object(id=post_id)
