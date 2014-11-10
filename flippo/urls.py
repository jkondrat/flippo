from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.core.cache import get_cache
from flippo import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'flippo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^items/', include('items.urls')),
    url(r'^$', views.index, name='index'),

    get_cache('default').clear()
)
