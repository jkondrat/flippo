import json
from django.core import serializers
from django.http import HttpResponse

# Create your views here.
from django.template import loader, RequestContext
from items.helper import get_item_or_none, fetch_all_info, PriceFetcher


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


def refresh_prices(request, ids):
    PriceFetcher.fetch([int(s) for s in ids.split(',')])
    response_data = dict()
    response_data['result'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def refresh_all_prices(request):
    response_data = dict()
    if PriceFetcher.working:
        response_data['result'] = 'busy'
    else:
        PriceFetcher.fetch_all()
        response_data['result'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def refresh_all_info(request):
    fetch_all_info()
    response_data = dict()
    response_data['result'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def refresh_status(request):
    response_data = dict()
    response_data['progress'] = PriceFetcher.progress
    response_data['curr'] = PriceFetcher.curr
    response_data['total'] = PriceFetcher.total
    response_data['working'] = PriceFetcher.working
    return HttpResponse(json.dumps(response_data), content_type="application/json")
