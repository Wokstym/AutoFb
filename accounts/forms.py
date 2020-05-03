import facebook
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class InsertToken(forms.Form):
    token = forms.CharField(label='Token', max_length=254, required=True)
    page_id = forms.CharField(label='Page ID', max_length=254, required=True)


def validate_token_page_id(token, page_id):
    try:
        graph = facebook.GraphAPI(token)
        default_info = graph.get_object(id=page_id, fields='posts')
        return True
    except:
        return False
