# -*- coding: utf-8 -*-
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404, render_to_response
from blog.models import *
from django.http import HttpResponseRedirect
from django.forms import ModelForm
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
import time
from calendar import month_name

# main view for the posts
def main(request):
    posts = Post.objects.all().order_by("-created")
    paginator = Paginator(posts, 5)

    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        posts = paginator.page(page)
    except (InvalidPage, EmptyPage):
        posts = paginator.page(paginator.num_pages)
    d = dict(posts=posts, user=request.user,
             post_list=posts.object_list, months=mkmonth_lst())

    return render_to_response("list.html", d)

def post(request, id, slug):
    post = Post.objects.get(pk=id)
    comments = Comment.objects.filter(post=post).order_by("-created")
    try:
        poll = Poll.objects.get( post = post )
    except Poll.DoesNotExist:
        poll = None
    d = dict(post=post, comments=comments, form=CommentForm(), user=request.user,
             creator=post.creator, months=mkmonth_lst(), poll=poll, slug=slug)
    d.update(csrf(request))
    return render_to_response("post.html", d)

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ["post"]

def mkmonth_lst():
    """Make a list of months to show archive links."""

    if not Post.objects.count(): return []

    # s et up vars
    year, month = time.localtime()[:2]
    first = Post.objects.order_by("created")[0]
    fyear = first.created.year
    fmonth = first.created.month
    months = []

    # loop over years and months
    for y in range(year, fyear-1, -1):
        start, end = 12, 0
        if y == year: start = month
        if y == fyear: end = fmonth-1

        for m in range(start, end, -1):
            months.append((y, m, month_name[m]))
    return months

def month(request, year, month):
    """Monthly archive."""
    posts = Post.objects.filter(created__year=year, created__month=month)
    d = dict(post_list=posts, user=request.user,
             months=mkmonth_lst(), archive=True)
    return render_to_response("list.html", d)

def add_comment(request, id, slug):
    """Add a new comment."""
    p = request.POST

    if p.has_key("body") and p["body"]:
        user = request.user
        if user.is_anonymous():
            author = "Anon"
        else:
            author = User.objects.get(username = user.username)

        comment = Comment(post=Post.objects.get(pk=id))
        cf = CommentForm(p, instance=comment)
        cf.fields["author"].required = False

        comment = cf.save(commit=False)
        comment.author = author
        comment.save()
    return HttpResponseRedirect(reverse("blog.views.post", args=[id, slug]))

def delete_comment(request, post_pk, pk=None):
    """Delete comment(s) with primary key `pk` or with pks in POST."""
    post = Post.objects.get(pk=post_pk)
    slug = post.slug
    if request.user.is_staff:
        if not pk: pklst = request.POST.getlist('delete')
        else: pklst = [pk]

        for pk in pklst:
            Comment.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse("blog.views.post", args=[post_pk, slug]))

#view to vote on the poll
def vote(request, post_pk):
    global choice
    poll = get_object_or_404(Poll, pk=post_pk)
    post = Post.objects.get(pk=post_pk)
    slug = post.slug
    try:
        selected_choice = poll.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return HttpResponseRedirect(reverse("blog.views.post", args=[poll.post.pk]))
    else:
        selected_choice.votes += 1
        poll.total_votes += 1
        selected_choice.save()
        poll.voted = True
        poll.save()

        choices = list(poll.choice_set.all())
        for choice in choices:
            percent = choice.votes*100/poll.total_votes
            choice.percentage = percent
            choice.save()

        return HttpResponseRedirect(reverse("blog.views.post", args=[poll.post.pk, slug]))

#view for the results of the poll:
def results(request, post_pk):
    post = Post.objects.get(pk=post_pk)
    slug = post.slug
    return HttpResponseRedirect(reverse("blog.views.post", args=[post_pk, slug]))

def vote_again(request, post_pk):
    try:
        p = get_object_or_404(Poll, post_id=post_pk)
    except (KeyError, Poll.DoesNotExist):
        pass
    else:
        p.voted = False
        p.save()
    post = Post.objects.get(pk=post_pk)
    slug = post.slug
    return HttpResponseRedirect(reverse("blog.views.post", args=[post_pk, slug]))




















