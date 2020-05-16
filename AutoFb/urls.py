from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from accounts import views as accounts_view
from home import views as home_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/', RedirectView.as_view(url='0', permanent=False), name='home'),
    path('home/<int:page_number>', include('home.urls'), name='home'),
    path('home/<int:page_number>/<slug:after>', include('home.urls'), name='home'),
    path('signup/', accounts_view.signup, name='signup'),
    path('add_page/', accounts_view.get_token, name='add_page'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('', home_view.start_page, name='start'),
    path('admin/', admin.site.urls, name='admin'),
    path('management/', home_view.management_page, name='management'),
    path('management/<int:page_number>/', home_view.management_page, name='management'),
    path('management/banned_words/<int:page_number>/', home_view.banned_words_page, name='banned_words'),
    path('pages/', home_view.pages, name='pages'),
    path('statistics/<int:page_number>/', home_view.statistics, name='statistics'),
    path('statistics/commenters/<int:page_number>/', home_view.top_commenters, name='Top 5 commenters'),
    path('statistics/liked/<int:page_number>/', home_view.top_liked_posts, name='Top 5 liked posts'),
    path('statistics/shared/<int:page_number>/', home_view.top_shared_posts, name='Top 5 shared posts'),
    path('statistics/commented/<int:page_number>/', home_view.top_commented_posts, name='Top 5 commented posts'),
    path('management/add_post/<int:page_number>/', home_view.add_post, name='add_post')
]
