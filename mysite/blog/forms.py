from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
    """Django form Email"""
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    """Django form Comment"""
    class Meta:
        """docstring for Meta."""
        model = Comment
        fields = ('name', 'email', 'body')

class SearchForm(forms.Form):
    """Django form SearchForm"""
    query = forms.CharField(label=" ")
