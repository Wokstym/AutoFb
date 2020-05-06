from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from accounts import views as accounts_view
from home import views as home_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/', RedirectView.as_view(url='0', permanent=False), name='index'),
    path('home/<int:page_number>/', include('home.urls'), name='home'),
    path('signup/', accounts_view.signup, name='signup'),
    path('add_page/', accounts_view.get_token, name='add_page'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('', home_view.start_page, name='start'),
    path('admin/', admin.site.urls, name='admin'),
    path('management/', home_view.management_page, name='management'),
    path('management/<int:page_number>/', home_view.management_page, name='management'),
    path('statistics/<int:page_number>/', home_view.statistics_page, name='statistics'),
    path('pages/', home_view.pages, name='pages'),
]
