from django.conf.urls import patterns, url

from items import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'([0-9]+)/$', views.item, name='item'),
    url(r'refresh/all-info/$', views.refresh_all_info, name='refreshAllInfo'),
    url(r'refresh/all-prices/$', views.refresh_all_prices, name='refreshAllPrices'),
    url(r'refresh/prices/([\w\,]+)$', views.refresh_prices, name='refreshPrices'),
    url(r'refresh/status/$', views.refresh_status, name='refreshStatus'),
)