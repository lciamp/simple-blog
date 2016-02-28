# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import User
from django.template.defaultfilters import slugify
from django.db.models import permalink

# Post class
class Post(models.Model):
    title = models.CharField(max_length=60)
    slug = models.SlugField()
    description = models.CharField(max_length=200)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User)

    #auto create a slug
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)

        super(Post, self).save(*args, **kwargs)

    def display_mySafeField(self):
        return mark_safe(self.body)

    def __unicode__(self):
        return self.title

# Admin class

class PostAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_filter = ('created',)
    fields = ('title', 'creator', 'description', 'body')

admin.site.register(Post, PostAdmin)

# Comment class
class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=60)
    body = models.TextField(max_length=500)
    post = models.ForeignKey(Post)
    #creator = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return unicode("%s: %s" % (self.post, self.body[:60]))

# Comment Admin class
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'body')
    search_fields = ('post', 'author')
    list_filter = ('post', 'author')
    fields = ('author', 'body')

admin.site.register(Comment, CommentAdmin)

# Poll for the Post
class Poll(models.Model):
    question = models.CharField(max_length=200)
    total_votes = models.DecimalField(default=0.0, max_digits=5, decimal_places=2)
    post = models.ForeignKey(Post)
    voted = models.BooleanField(default=False)
    #voter = models.ForeignKey(User, blank=True, null=True)

    @permalink
    def get_absolute_url(self):
        return ('article', (), {
            'slug': Post.slug,
            'id': Poll.post.pk,
            })

    def __unicode__(self):
        return self.question


# Choice for the poll
class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length=200)
    votes = models.DecimalField(default=0.0, max_digits=5, decimal_places=2)
    percentage = models.DecimalField(default=0.0, max_digits=5, decimal_places=2)

    def __unicode__(self):
        return self.choice

class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 3

class PollAdmin(admin.ModelAdmin):
    fieldset = [
        (None, {'fields': ['question']}),
        ('votes', {'fields': ['total_votes']}),
        ('poll', {'fields': ['poll'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question', 'post')

admin.site.register(Poll, PollAdmin)




