import json
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, Http404

# Create your views here.
from django.template import loader, RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from items.helper import get_item_or_none, fetch_all_info, PriceFetcher
from items.models import WatchList, Item


class UserMixin(object):
    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def dispatch(self, *args, **kwargs):
        return super(UserMixin, self).dispatch(*args, **kwargs)

class AdminMixin(object):
    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise Http404
        return super(AdminMixin, self).dispatch(*args, **kwargs)


class WatchListView(UserMixin, TemplateView):
    template_name = "watchlist.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        try:
            watchlist = WatchList.objects.get(user=self.request.user)
        except WatchList.DoesNotExist:
            watchlist = WatchList()
            watchlist.user = self.request.user
            watchlist.save()
        context['items'] = watchlist.items.all().order_by('-profit_percent')
        context['request'] = self.request
        return context


def watchlist_add(request, id):
    try:
        watchlist = WatchList.objects.get(user=request.user)
    except WatchList.DoesNotExist:
        watchlist = WatchList()
        watchlist.user = request.user
    try:
        item = Item.objects.get(item_id=id)
        watchlist.items.add(item)
        watchlist.save()
        return HttpResponse()
    except:
        return Http404


def watchlist_remove(request, id):
    try:
        watchlist = WatchList.objects.get(user=request.user)
        item = Item.objects.get(item_id=id)
        watchlist.items.remove(item)
        watchlist.save()
        return HttpResponse()
    except:
        return Http404



def index(request):
    return HttpResponse("Hello, world. You're at the items index.")


def item(request, id):
    template = loader.get_template('item.html')
    context = RequestContext(request, {
        'item': get_item_or_none(id)
    })
    return HttpResponse(template.render(context))


def refresh_price(request, id):
    response_data = dict()
    item = PriceFetcher().fetch_single(id)
    response_data['item'] = serializers.serialize('json', [item, ])
    response_data['market'] = serializers.serialize('json', [item.market, ])
    response_data['result'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def refresh_watchlist(request):
    response_data = dict()
    if request.user.is_authenticated():
        try:
            watchlist = WatchList.objects.get(user=request.user)
            PriceFetcher().fetch([i.item_id for i in watchlist.items.all()])
        except WatchList.DoesNotExist:
            pass
        response_data['result'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def refresh_prices(request, ids):
    response_data = dict()
    if request.user.is_authenticated():
        PriceFetcher().fetch([int(s) for s in ids.split(',')])
        response_data['result'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def refresh_all_prices(request):
    response_data = dict()
    if request.user.is_authenticated():
        if PriceFetcher.get_progress()['working']:
            response_data['result'] = 'busy'
        else:
            PriceFetcher.fetch_all()
            response_data['result'] = 'ok'
    else:
        response_data['result'] = 'unauthorized'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def refresh_all_info(request):
    fetch_all_info()
    response_data = dict()
    response_data['result'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def refresh_status(request):
    response_data = PriceFetcher.get_progress()
    return HttpResponse(json.dumps(response_data), content_type="application/json")
