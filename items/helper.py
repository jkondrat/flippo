import json
from django.db import transaction
from pip._vendor.requests.packages import urllib3
import time
from items.models import Item, Details, MarketInfo


def get_flippable():
    market = MarketInfo.objects.filter(sell_price__gte=200).filter(buy_quantity__gte=200).filter(sell_quantity__gte=200)
    return Item.objects.filter(market__in=market)


def get_item_or_none(id):
    try:
        return Item.objects.get(item_id=id)
    except Item.DoesNotExist:
        return None


def get_json(url):
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    return json.loads(r.data)


# prepare urls for fetching (up to 200 ids)
def prepare_urls(base_url, ids):
    urls = []
    cnt = 0
    url = base_url
    for id in ids:
        if cnt < 200:
            url = url + str(id) + ","
            cnt += 1
        else:
            urls.append(url[:-1])
            url = base_url
            cnt = 0
    if url != base_url:
        urls.append(url[:-1])
    return urls


def parse_info(json_obj):
    try:
        item = Item.objects.get(item_id=json_obj['id'])
    except Item.DoesNotExist:
        item = Item()
    item.item_id = json_obj['id']
    item.name = json_obj['name']
    item.icon = json_obj['icon']
    item.type = json_obj['type']
    item.rarity = json_obj['rarity']
    item.level = json_obj['level']
    item.vendor_value = json_obj['vendor_value']
    item.flags = json_obj['flags']
    item.game_types = json_obj['game_types']
    item.restrictions = json_obj['restrictions']
    #optionals
    try:
        item.description = json_obj['description']
    except KeyError:
        pass
    try:
        item.default_skin = json_obj['default_skin']
    except KeyError:
        pass
    try:
        details_content = json_obj['details']
        if item.details is not None:
            details = item.details
        else:
            details = Details()
        details.content = details_content
        details.save()
        item.details = details
    except KeyError:
        pass
    item.save()


def fetch_all_info():
    ids = get_json('https://api.guildwars2.com/v2/commerce/prices/')
    urls = prepare_urls('http://api.guildwars2.com/v2/items?ids=', ids)
    i = 0
    j = 0
    for url in urls:
        i += 1
        items = get_json(url)
        for json_obj in items:
            j += 1
            parse_info(json_obj)
        print(str(i) + " out of " + str(len(urls)))


def parse_price(json_obj):
    try:
        item = Item.objects.get(item_id=json_obj['id'])
    except Item.DoesNotExist:
        print('item not found, id:' + str(json_obj['id']))
        return
    if item.market is not None:
        market = item.market
    else:
        market = MarketInfo()
    market.buy_price = json_obj['buys']['unit_price']
    market.buy_quantity = json_obj['buys']['quantity']
    market.sell_price = json_obj['sells']['unit_price']
    market.sell_quantity = json_obj['sells']['quantity']
    market.save()
    item.market = market
    item.profit = item.calc_profit()
    item.profit_percent = item.calc_profit_percent()
    item.save()


class PriceFetcher:
    progress = 0
    curr = 0
    total = 0

    @staticmethod
    def fetch_all():
        ids = get_json('https://api.guildwars2.com/v2/commerce/prices/')
        PriceFetcher.fetch(ids)

    @staticmethod
    @transaction.commit_manually
    def fetch(ids):
        urls = prepare_urls('http://api.guildwars2.com/v2/commerce/prices?ids=', ids)
        PriceFetcher.total = len(ids)
        PriceFetcher.curr = 0
        PriceFetcher.progress = 0.0
        for url in urls:
            dl = 0.0
            pr = 0.0
            start = time.time()
            prices = get_json(url)
            dl += time.time() - start
            start = time.time()
            for json_obj in prices:
                parse_price(json_obj)
                PriceFetcher.curr += 1
                PriceFetcher.progress = PriceFetcher.curr * 100 / PriceFetcher.total
            pr += time.time() - start
            #print('fetching prices, dl: ' + str(int(round(dl * 1000))) + ' pr:' + str(int(round(pr * 1000))))
            transaction.commit()