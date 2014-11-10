from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse

# Create your views here.
from django.template import loader, RequestContext
from items.helper import fetch_all_info, PriceFetcher, get_flippable
from items.models import Item, MarketInfo


def index(request):
    items_list = Item.objects.all()
    if items_list.count() == 0:
        fetch_all_info()
        PriceFetcher.fetch_all()
        items_list = Item.objects.all()
    if len(request.GET.get('q', '')) > 0:
        items_list = items_list.filter(name__icontains=request.GET.get('q', ''))
    if len(request.GET.get('type', '')) > 0:
        items_list = items_list.filter(type__icontains=request.GET.get('type', ''))
    if len(request.GET.get('rarity', '')) > 0:
        items_list = items_list.filter(rarity__icontains=request.GET.get('rarity', ''))
    if len(request.GET.get('level', '')) > 0:
        items_list = items_list.filter(level=request.GET.get('level', ''))
    if len(request.GET.get('count', '')) > 0:
        try:
            market = MarketInfo.objects.filter(sell_quantity__gte=request.GET.get('count', ''))
            items_list = items_list.filter(market__in=market)
        except ValueError:
            pass
    if len(request.GET.get('buy_price', '')) > 0:
        try:
            market = MarketInfo.objects.filter(buy_price__gte=request.GET.get('buy_price', ''))
            items_list = items_list.filter(market__in=market)
        except ValueError:
            pass
    template = loader.get_template('index.html')
    paginator = Paginator(items_list.order_by('-profit_percent'), 200)
    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    context = RequestContext(request, {
        'paginator': paginator,
        'items': items,
        'request': request
    })
    return HttpResponse(template.render(context))