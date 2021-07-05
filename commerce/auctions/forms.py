from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):

    class meta(UserCreationForm):
        model= User
        fields = UserCreationForm.Meta.fields + ('first','last',)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model=User
        fields= UserCreationForm.Meta.fields
