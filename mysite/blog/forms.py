from django import forms
from .models import Comment



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment  # для ModelForm обязательно указывать в классе Meta модель, на основе которой будет строиться форма
        fields = ['name', 'email', 'body']  # это поля, отображаемые в html форме(не точно)


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)


class SearchForm(forms.Form):
    query = forms.CharField()
