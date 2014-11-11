from django.conf.urls import patterns, include, url
from django.contrib import admin
from flippo import views
from flippo.views import LoginView, LogoutView, RegisterView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'flippo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^items/', include('items.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView, name='logout'),
    url(r'^register/$', RegisterView.as_view(), name='register'),

)
