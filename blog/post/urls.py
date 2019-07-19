from django.conf.urls import url
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
    url(r'^post/(?P<postid>\d+)/', views.PostView.as_view(),
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
        )
]
