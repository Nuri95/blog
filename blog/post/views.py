# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, FormView, DeleteView

from forms import PostForm, LoginForm
from models import Post


class IndexView(TemplateView):
    template_name = 'post/index.html'

    def test(self, kwargs, post_filter=False):
        posts = Post.objects.all()

        if post_filter:
            posts = posts.filter(user=self.request.user)

        posts = posts.order_by('-date')
        paginator = Paginator(posts, 10)

        try:
            page_number = self.request.GET.get('page', default=1)
            posts = paginator.page(page_number)
        except PageNotAnInteger:
            page_number = 1
            posts = paginator.page(1)
        except EmptyPage:
            posts = []

        # models = [ShortPostModel(post) for post in posts]
        context = super(IndexView, self).get_context_data(**kwargs)
        context['count'] = paginator.count
        context['page_size'] = 10
        context['page_number'] = int(page_number)
        context['page_previous'] = int(page_number) - 1
        context['posts'] = posts

        if context['page_size'] * context['page_number'] < context['count']:
            context['page_next'] = int(page_number) + 1
        else:
            context['page_next'] = None

        return context

    def get_context_data(self, **kwargs):
        return self.test(kwargs)

    def dispatch(self, request, *args, **kwargs):

        if not self.request.user.is_authenticated():
            return redirect(reverse('view_login'))

        return super(IndexView, self).dispatch(request, *args, **kwargs)


# class ShortPostModel:
#     def __init__(self, post):
#         self.id = post.id
#         self.date = post.date
#         self.title = post.title
#         self.user = post.user
#         self.body = post.body[:100]


class PostLikeView(View):
    def post(self, request, *args, **kwargs):
        print request
        print args
        print kwargs
        return HttpResponse()



class PostMyView(IndexView):
    template_name = 'post/index.html'

    def get_context_data(self, **kwargs):
        return self.test(kwargs, True)


class PostUserView(TemplateView):
    template_name = 'post/index.html'

    def get_context_data(self, **kwargs):
        posts = Post.objects.all()
        userid = kwargs['userid']
        if userid:
            posts = posts.filter(user_id=userid)
        context = super(PostUserView, self).get_context_data(**kwargs)
        context['posts'] = posts

        return context


class PostView(TemplateView):
    template_name = 'post/post.html'

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=kwargs['postid'])

        return context


class PostDeleteView(DeleteView):
    model = Post
    pk_url_kwarg = 'postid'

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()

        return HttpResponse()

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        object = self.get_object()

        if object.user == user:
            return super(PostDeleteView, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404()


class LoginView(FormView):
    template_name = 'post/login.html'
    form_class = LoginForm

    def get_success_url(self):
        return reverse('view_posts')

    def form_valid(self, form):
        username = form.cleaned_data['login']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
        else:
            form.add_error('password',
                           'Не удается войти. Проверьте логин и пароль.'
                           )

            return self.render_to_response(self.get_context_data(form=form))
        return super(LoginView, self).form_valid(form)


class RegistrationView(FormView):
    template_name = 'post/registration.html'
    form_class = UserCreationForm

    def get_success_url(self):
        return reverse('view_posts')

    def form_valid(self, form):
        new_user = form.save()
        login(self.request, new_user)

        return super(RegistrationView, self).form_valid(form)


class LogoutView(View):
    @method_decorator(login_required())
    def post(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponse()


class PostEditView(FormView):
    template_name = 'post/edit.html'
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):

        try:
            self.post_object = Post.objects.get(id=kwargs['postid'],
                                                user=request.user)
        except Post.DoesNotExist:
            raise Http404

        return super(PostEditView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super(PostEditView, self).form_valid(form)

    def get_success_url(self):
        return reverse('view_posts')

    def get_form_kwargs(self):
        post_edit = super(PostEditView, self).get_form_kwargs()
        post_edit['instance'] = self.post_object

        return post_edit


class PostCreateView(FormView):
    template_name = 'post/create.html'
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return redirect(reverse('view_login'))
        return super(PostCreateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super(PostCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('view_posts')

    def get_form_kwargs(self):
        new_post = super(PostCreateView, self).get_form_kwargs()
        new_post['instance'] = Post(date=timezone.now(),
                                    user=self.request.user)

        return new_post
