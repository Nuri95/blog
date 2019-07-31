from django import forms

from post.models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body')


class LoginForm(forms.Form):
    login = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)

