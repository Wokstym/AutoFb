import facebook
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from home.models import BannedWord
from home.utils import datetime_to_string


class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class InsertToken(forms.Form):
    token = forms.CharField(label='Token', max_length=254, required=True)
    page_id = forms.CharField(label='Page ID', max_length=254, required=True)


class InsertWord(forms.Form):
    word = forms.CharField(label='Word', max_length=100, required=True)

    class Meta:
        model = BannedWord
        fields = 'word'


class InsertPost(forms.Form):
    message = forms.CharField(label='Message', max_length=512, required=True)
    image = forms.ImageField(label='Image', required=False)
    date = forms.CharField(label='Date', max_length=17, initial=datetime_to_string(), required=True)


def validate_token_page_id(token, page_id):
    try:
        graph = facebook.GraphAPI(token)
        default_info = graph.get_object(id=page_id, fields='posts')
        return True
    except:
        return False


def validate_word(word):
    if " " in word:
        return False

    return True
