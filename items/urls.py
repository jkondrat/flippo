from django.conf.urls import patterns, url

from items import views
from items.views import WatchListView

urlpatterns = patterns('',
    url(r'^$', views.index, name='itemIndex'),
    url(r'^([0-9]+)/$', views.item, name='item'),
    url(r'refresh/all-prices/$', views.refresh_all_prices, name='refreshAllPrices'),
    url(r'refresh/status/$', views.refresh_status, name='refreshStatus'),
    url(r'refresh/price/([0-9]+)/$', views.refresh_price, name='refreshPrice'),
    url(r'watchlist/$', WatchListView.as_view(), name='watchlist'),
)