# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, FormView, DeleteView

from forms import PostForm, LoginForm, CommentForm
from models import Post, Comment


class IndexView(TemplateView):
    template_name = 'post/index.html'

    def attach_filter(self, posts, **kwargs):
        return posts

    def attach_sort(self, posts, **kwargs):
        return posts.order_by('-date')

    def get_context_data(self, **kwargs):
        # posts = Post.objects.all()
        # print posts
        posts = Post.objects.annotate(number_of_comments=Count('comment'))
        print 'posts= ', posts
        posts = self.attach_filter(posts, **kwargs)
        posts = self.attach_sort(posts, **kwargs)
        paginator = Paginator(posts, 10)

        try:
            page_number = self.request.GET.get('page', default=1)
            posts = paginator.page(page_number)
        except PageNotAnInteger:
            page_number = 1
            posts = paginator.page(1)
        except EmptyPage:
            posts = []

        for post in posts:
            post.is_liked = post.is_liked_by(self.request.user)

        # models = [ShortPostModel(post) for post in posts]
        context = super(IndexView, self).get_context_data(**kwargs)
        print 'context= ', context
        context['count'] = paginator.count
        context['page_size'] = 10
        context['page_number'] = int(page_number)
        context['page_previous'] = int(page_number) - 1
        context['posts'] = posts
        context['url_name']=self.request.path #resolve(self.request.path).url_name

        if context['page_size'] * context['page_number'] < context['count']:
            context['page_next'] = int(page_number) + 1
        else:
            context['page_next'] = None

        return context


    def dispatch(self, request, *args, **kwargs):

        if not self.request.user.is_authenticated():
            return redirect(reverse('view_login'))

        return super(IndexView, self).dispatch(request, *args, **kwargs)



class PostLikeView(View):

    def post(self, request, *args, **kwargs):
        postid = kwargs['postid']
        user = request.user
        post = get_object_or_404(Post, id=postid)

        if post.likes.filter(id=request.user.id):
            post.likes.remove(user)
            is_liked = False
        else:
            post.likes.add(user)
            is_liked = True

        post.save()

        context = {
            'postId': postid,
            'isLiked': is_liked,
            'totalLikes': post.total_likes
        }
        return JsonResponse(context)


class PostCommentView(FormView):
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        try:
            self.post_object = Post.objects.get(id=request.POST.get('post_id'))
        except Post.DoesNotExist:
            raise Http404

        return super(PostCommentView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        return JsonResponse(form.save().as_json())

    def get_form_kwargs(self):
        new_comment = super(PostCommentView, self).get_form_kwargs()
        new_comment['instance'] = Comment(date=timezone.now(),
                                          user=self.request.user,
                                          post=self.post_object)
        return new_comment


class PostView(TemplateView):
    template_name = 'post/post.html'

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=kwargs['postid'])
        context['post'].is_liked = context['post'].is_liked_by(self.request.user)
        print 'context =', context
        # context['blabla'] = get_formatted_date(context['post'].date)
        return context


class PostBestView(IndexView):
    def attach_sort(self, posts, **kwargs):
        return posts.annotate(like_count=Count('likes')).order_by('-like_count')


class PostMyView(IndexView):
    template_name = 'post/index.html'

    def attach_filter(self, posts, **kwargs):
        return posts.filter(user=self.request.user)


class PostUserView(IndexView):
    template_name = 'post/index.html'

    def attach_filter(self, posts, **kwargs):
        return posts.filter(user=kwargs['user'])

    def get_context_data(self, **kwargs):
        userid = kwargs['userid']
        kwargs['user'] = get_object_or_404(User, id=userid)
        return super(PostUserView, self).get_context_data(**kwargs)


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


class PostCommentDeleteView(PostDeleteView):
    model = Comment
    pk_url_kwarg = 'commentid'


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
