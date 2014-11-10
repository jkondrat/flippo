from django.db import models


class Listing(models.Model):
    count = models.IntegerField()
    unit_price = models.IntegerField()
    quantity = models.IntegerField()


class MarketInfo(models.Model):
    buy_price = models.IntegerField(null=True)
    buy_quantity = models.IntegerField(null=True)
    sell_price = models.IntegerField(null=True)
    sell_quantity = models.IntegerField(null=True)
    buys = models.ManyToManyField(Listing, related_name='market_buys')
    sells = models.ManyToManyField(Listing, related_name='market_sells')
    last_updated = models.DateTimeField(auto_now=True)


class Details(models.Model):
    content = models.TextField(null=True)

    def __str__(self):              # __unicode__ on Python 2
        return self.content.encode("UTF-8")


class Item(models.Model):
    item_id = models.IntegerField()
    market = models.ForeignKey(MarketInfo, null=True)
    name = models.CharField(max_length=100, null=True)
    icon = models.CharField(max_length=150, null=True)
    description = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=50, null=True)
    rarity = models.CharField(max_length=50, null=True)
    level = models.IntegerField(null=True)
    vendor_value = models.IntegerField(null=True)
    default_skin = models.IntegerField(null=True)
    flags = models.CharField(max_length=150, null=True)
    game_types = models.CharField(max_length=100, null=True)
    restrictions = models.CharField(max_length=150, null=True)
    details = models.ForeignKey(Details, null=True)
    # custom fields
    profit = models.IntegerField(null=True)
    profit_percent = models.FloatField(null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):              # __unicode__ on Python 2
        return self.name.encode("UTF-8")

    def calc_profit(self):
        if self.market is not None:
            net_sell_price = 0.85 * (self.market.sell_price - 1)
            if self.market.buy_price > self.vendor_value and net_sell_price > self.vendor_value:
                return int(net_sell_price - (self.market.buy_price + 1))
        return 0

    def calc_profit_percent(self):
        if self.market is not None and self.market.buy_price > 0:
            return round((self.calc_profit() * 100.0) / (self.market.buy_price + 1), 2)
        return 0
