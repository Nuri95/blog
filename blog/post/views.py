# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator, PageNotAnInteger
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, FormView

from forms import PostForm, LoginForm
from models import Post


class IndexView(TemplateView):
    template_name = 'post/index.html'

    def get_context_data(self, **kwargs):
        posts = Post.objects.order_by('-date')
        paginator = Paginator(posts, 10)
        try:
            page_number = self.request.GET.get('page', default=1)
            posts = paginator.page(page_number)
        except PageNotAnInteger:
            page_number = 1
            posts = paginator.page(1)
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

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return redirect(reverse('view_login'))
        return super(IndexView, self).dispatch(request, *args, **kwargs)

    # @method_decorator(login_required)
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)


class PostView(TemplateView):
    template_name = 'post/post.html'

    @method_decorator(login_required())
    def delete(self, request, *args, **kwargs):
        postid = kwargs['postid']
        post = get_object_or_404(Post, pk=postid)
        if post.user == request.user:
            post.delete()
            return HttpResponse()
        else:
            raise Http404()

    def get(self, request, *args, **kwargs):
        postid = kwargs['postid']
        try:
            post = Post.objects.get(id=postid)
        except Post.DoesNotExist:
            raise Http404()
        return self.render_to_response(self.get_context_data(post=post))

# class LoginView(TemplateView):
#     template_name = 'post/login.html'
#
#     def dispatch(self, request, *args, **kwargs):
#         if self.request.user.is_authenticated():
#             return redirect(reverse('view_posts'))
#         return super(LoginView, self).dispatch(request, *args, **kwargs)
#
#     def get(self, *args, **kwargs):
#         if self.request.user.is_authenticated():
#             return redirect(reverse('view_posts'))
#         context = self.get_context_data(**kwargs)
#         return self.render_to_response(context)
#
#     def post(self, *args, **kwargs):
#         if self.request.user.is_authenticated():
#             return HttpResponse(status=400)
#         username = self.request.POST['login']
#         password = self.request.POST['password']
#         user = authenticate(username=username, password=password)
#         print 'user', user
#         if user:
#             if user.is_active:
#                 login(self.request, user)
#                 return redirect(reverse('view_posts'))
#             else:
#                 context = self.get_context_data(**kwargs)
#                 context['error'] = 'User not active'
#                 return self.render_to_response(context)
#         else:
#             context = self.get_context_data(**kwargs)
#             context['error'] = 'Invalid credentials'
#             return self.render_to_response(context)


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


class RegistrationView(TemplateView):
    template_name = 'post/registration.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect(reverse('view_posts'))
        context = self.get_context_data()
        context['form'] = UserCreationForm()
        return self.render_to_response(context)

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect(reverse('view_posts'))
        form = UserCreationForm(self.request.POST)
        if form.is_valid():
            new_user = form.save()
            login(self.request, new_user)
            return redirect(reverse('view_posts'))
        return self.render_to_response(self.get_context_data(form=form))


class LogoutView(View):
    @method_decorator(login_required())
    def post(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponse()


# class PostEditView(TemplateView):
#     template_name = 'post/edit.html'
#
#     def post(self, request, *args, **kwargs):
#         postid = kwargs['postid']
#         post = get_object_or_404(Post, pk=postid)
#         if post.user == request.user:
#             form = PostForm(request.POST, instance=post)
#             if form.is_valid():
#                 form.save()
#                 return redirect(reverse('view_posts'))
#             return render_to_response(self.get_context_data(form=form))
#         else:
#             raise Http404()
#
#     def get(self, request, *args, **kwargs):
#         postid = kwargs['postid']
#         post = get_object_or_404(Post, pk=postid)
#         if post.user == request.user:
#             return self.render_to_response(self.get_context_data(
#                 post=post,
#                 form=PostForm(instance=post))
#             )
#         else:
#             raise Http404()


class PostEditView(FormView):
    template_name = 'post/edit.html'
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs['postid'])
        if self.post_object.user == request.user:
            return super(PostEditView, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404

    def form_valid(self, form):
        form.save()
        return super(PostEditView, self).form_valid(form)

    def get_success_url(self):
        return reverse('view_posts')

    def get_form_kwargs(self):
        x = super(PostEditView, self).get_form_kwargs()
        x['instance'] =self.post_object
        return x


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
        x = super(PostCreateView, self).get_form_kwargs()
        x['instance'] = Post(date=timezone.now(),
                             user=self.request.user)
        return x


# class PostCreateView(TemplateView):
#     template_name = 'post/create.html'
#
#     def get(self, *args, **kwargs):
#         if not self.request.user.is_authenticated():
#             return redirect(reverse('view_login'))
#         context = self.get_context_data(**kwargs)
#         print 'context=', context
#         return self.render_to_response(context)
#
#     @method_decorator(login_required())
#     def post(self, request, *args, **kwargs):
#         post = Post(title=self.request.POST['title'],
#                     body=self.request.POST['body'],
#                     date=timezone.now(),
#                     user=request.user)
#
#         form = PostForm(request.POST, instance=post)
#
#         if form.is_valid():
#             form.save()
#         else:
#             return self.render_to_response(self.get_context_data(form=form))
#         context = self.get_context_data(**kwargs)
#         context['user='] = request.user
#         return redirect(reverse('view_posts'))
#
