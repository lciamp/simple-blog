from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
from django.core.urlresolvers import reverse
admin.autodiscover()

urlpatterns = patterns('blog.views',
    ### main/index page
    url(r'^$', 'main', name='index'),

    ### url for the post.html
    url(r"^(\d+)/$", "post"),
    url(r'^(\d+)/([-\w\d]+)/$', 'post'),
    (r"^month/(\d+)/(\d+)/$", "month"),

    ### url for comments
    url(r'^add_comment/(\d+)/([-\w\d]+)/$', 'add_comment'),
    url(r'^delete_comment/(\d+)/$', 'delete_comment'),
    url(r'^delete_comment/(\d+)/(\d+)/$', 'delete_comment'),

    ### url for monthly archive
    url(r"^(\d+)/(\d+)/$", "month"),

    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    ### admin page
    url(r'^admin/', include(admin.site.urls)),

    ### polls
    url(r'^polls/results/(\d+)/$', 'results'),
    url(r'^polls/vote/(\d+)/$', 'vote'),
    url(r'^revote/(\d+)/$', 'vote_again'),
    url(r'^admin_tools/', include('admin_tools.urls')),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views', url(r'^static/(?P<path>.*)$', 'serve'),
                                )