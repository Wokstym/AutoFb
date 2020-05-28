# Project from Programming in Python

[![](https://img.shields.io/badge/Django-2.2.12-red)](https://www.djangoproject.com)
[![](https://img.shields.io/badge/django_bootstrap4-1.1.1-blue)](https://pypi.org/project/django-bootstrap4/)
[![](https://img.shields.io/badge/django_widget_tweaks-1.4.8-green)](https://pypi.org/project/django-widget-tweaks/)
[![](https://img.shields.io/badge/facebook_sdk-3.1.0-orange)](https://pypi.org/project/facebook-sdk/)
[![](https://img.shields.io/badge/djongo-1.3.1-yellow)](https://pypi.org/project/djongo/)
[![](https://img.shields.io/badge/dnspython-1.16.0-lightgrey)](https://pypi.org/project/dnspython/)
[![](https://img.shields.io/badge/Pillow-7.1.2-brown)](https://pypi.org/project/Pillow/)

Page used for automating tasks when managing pages, such as storing not allowed words, that with a push of a button are localized in comments and deleted in choosen post or all posts, liking all comments, deleteting and posting posts. You can also view statistics that are not avaible in facebook such as top 5 most commented, shared and liked posts or top 5 most active commenters.

## Showcase

![presentation gif](./presentation.gif)

## Setup

```bash
pip install -r requirements.txt
```

## Roadmap

### Lab 3 (April 7/9)

- [x] Django configuration (Grzesiek)
- [x] Database mongo atlas configuration (Grzesiek)

### Lab 4 (April 21/23)

- [x] Logging and registration (Grzesiek)
- [x] Token authorization and storage (Grzesiek)
- [x] Main page with posts (Ola)

### Lab 5 (May 5/7)

- [x] Statistics about top 5 commenters (Grzesiek)
- [x] Statistics about top 5 posts with biggest amount of likes/comment/shares (Grzesiek)
- [x] Ability to delete comments containing words from database (Ola)
- [x] Post deletion (Ola)
- [x] Liking all comments in a post/all posts (Ola)
- [x] Fanpage selection (Ola)

### Lab 6 (May 19/21)

- [x] Deletion of banned words from database (Ola)
- [x] Form for adding post with photo (Ola)
- [x] Uploading of photos (Ola)
- [x] Management of post by its id (Grzesiek)
- [x] Posts pagination (Grzesiek)
- [ ] Scheduling

### Project submission (June 2/4)

## Summary

Project teached us working in a team using branches, merging with master finished aspects and resolving conflicts, overall concept of using API for fetching and posting content and usage of django + mongodb database models, renderign views and Django template language.

We've done all the planned things except one - scheduling. We've tried to use many libraries but they didn't want to work with us.

### Ola

The project turned out to be quite time consuming due to problems with the Django version and access to facebook data. 
But despite this I think we're both happy with the result.
My knowledge of Python, Django and  mongodb has certainly expanded.
I will also remember for the future that the latest version is not always the best choice and that Python has a huge number of libraries that make life easier.


## Contributors ✨

<table>
  <tr>
    <td align="center"><a href="https://github.com/Wokstym"><img src="https://avatars2.githubusercontent.com/u/44115112?s=460&u=2fea6d808fb949060aa499dad3e3365608bb5c40&v=4" width="100px;" alt=""/><br /><sub><b>Grzegorz Poręba</b></sub></a><br />
    </td>
    <td align="center"><a href="https://github.com/alexmaz99"><img src="https://avatars2.githubusercontent.com/u/56346754?s=460&u=a0c3bd4ae7860a0694db0110f7b10d80434fecd4&v=4" width="100px;" alt=""/><br /><sub><b>Aleksandra Mazur</b></sub></a><br /></td>
  </tr>
</table>