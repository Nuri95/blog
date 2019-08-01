from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(),
        name='view_posts'
        ),
    url(r'^login$', views.LoginView.as_view(),
        name='view_login'
        ),
    url(r'^registration$', views.RegistrationView.as_view(),
        name='view_registration'
        ),
    url(r'^post/(?P<postid>\d+)/$', views.PostView.as_view(),
        name='view_post'
        ),
    url(r'^logout/$', views.LogoutView.as_view(),
        name='view_logout'
        ),
    url(r'^edit/(?P<postid>\d+)/$', views.PostEditView.as_view(),
        name='view_edit'
        ),
    url(r'^create/$', views.PostCreateView.as_view(),
        name='view_create'
        ),
    url(r'^post/(?P<postid>\d+)/delete/$', views.PostDeleteView.as_view(),
        name='view_delete'
        ),
    url(r'comment/(?P<commentid>\d+)/delete/$', views.PostCommentDeleteView.as_view(),
        name='view_delete_comment'
        ),
    url(r'^my/$', views.PostMyView.as_view(),
        name='view_my'
        ),
    url(r'^user-posts/(?P<userid>\d+)/$', views.PostUserView.as_view(),
        name='view_user'
        ),
    url(r'^like/(?P<postid>\d+)/$', login_required(views.PostLikeView.as_view()),
        name='view_like_post'
        ),
    url(r'^comment/new/$', views.PostCommentView.as_view(),
        name='view_comment_post'
        ),
    url(r'^best/$', views.PostBestView.as_view(),
        name='view_best'
        ),

]
