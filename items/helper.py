import json
import threading
import urllib
from django.core import cache
from django.core.cache import get_cache
from django.db import transaction
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
    r = urllib.urlopen(url).read()
    return json.loads(r)


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
    return item


class PriceFetcher:
    cache = get_cache('default')

    @classmethod
    def reset(cls, total):
        cls.cache.clear()
        cls.cache.set('counter', 0)
        cls.cache.set('progress', 0.0)
        cls.cache.set('total', total)

    @classmethod
    def increment_counter(cls, i):
        cls.cache.set('counter', cls.cache.get('counter') + i)
        if cls.cache.get('total') > 0:
            cls.cache.set('progress', cls.cache.get('counter') * 100 / cls.cache.get('total'))
        else:
            cls.cache.set('progress', 0.0)

    @classmethod
    def set_working(cls, working):
        cls.cache.set('working', working)

    @classmethod
    def get_progress(cls):
        data = dict()
        data['progress'] = cls.cache.get('progress', 0.0)
        data['curr'] = cls.cache.get('counter', 0)
        data['total'] = cls.cache.get('total', 0)
        data['working'] = cls.cache.get('working', False)
        return data

    def fetch_single(self, id):
        url = "http://api.guildwars2.com/v2/commerce/prices/" + str(id)
        price = get_json(url)
        return parse_price(price)

    @staticmethod
    @transaction.commit_manually
    def fetch_all():
        ids = get_json('https://api.guildwars2.com/v2/commerce/prices/')
        urls = prepare_urls('http://api.guildwars2.com/v2/commerce/prices?ids=', ids)
        PriceFetcher.reset(len(ids))
        PriceFetcher.set_working(True)
        for url in urls:
            dl = 0.0
            pr = 0.0
            i = 0
            start = time.time()
            prices = get_json(url)
            dl += time.time() - start
            start = time.time()
            for json_obj in prices:
                parse_price(json_obj)
                i += 1
            PriceFetcher.increment_counter(i)
            pr += time.time() - start
            print('fetching prices, dl: ' + str(int(round(dl * 1000))) + ' pr:' + str(int(round(pr * 1000))))
            transaction.commit()
        PriceFetcher.set_working(False)

    @transaction.commit_manually
    def fetch(self, ids):
        urls = prepare_urls('http://api.guildwars2.com/v2/commerce/prices?ids=', ids)
        for url in urls:
            prices = get_json(url)
            for json_obj in prices:
                parse_price(json_obj)
            transaction.commit()