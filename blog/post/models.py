# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    date = models.DateTimeField()
    user = models.ForeignKey(User)
    likes = models.ManyToManyField(User, blank=True, related_name='likes')
    # abc = models.ManyToOneRel()

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.title

    @property
    def total_likes(self):
        return self.likes.count()

    def is_liked_by(self, user):
        return self.likes.filter(id=user.id).exists()
