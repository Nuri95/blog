# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import dateformat
from django.utils.timezone import localtime


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    date = models.DateTimeField()
    user = models.ForeignKey(User)
    likes = models.ManyToManyField(User, blank=True, related_name='likes')

    # Post.objects.like_set.filter(is_active=True).count()
    # Like.is_active = False

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.title

    # @property
    def total_likes(self):
        print 'LIKE DB QUERY'
        return self.likes.count()

    def is_liked_by(self, user):
        return self.likes.filter(id=user.id).exists()

    @property
    def comments(self):
        return self.comment_set.order_by('-date')

    # @property
    # def total_comment(self):
    #     return self.comments.count()


class Comment(models.Model):
    post = models.ForeignKey(Post)
    comment = models.ForeignKey('self', related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    body = models.TextField()
    date = models.DateTimeField()
    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.body

    def as_json(self):
        return {
            'id': self.id,
            'postId': self.post.id,
            'body': self.body,
            'date': dateformat.format(localtime(self.date), settings.DATETIME_FORMAT),
            'author': {
                'id': self.user.id,
                'username': self.user.username
            }
        }

    # def formatted_date(self):
    #     return dateformat.format(self.date, settings.DATETIME_FORMAT)


# def get_formatted_date(date):
#     return dateformat.format(date, settings.DATETIME_FORMAT)