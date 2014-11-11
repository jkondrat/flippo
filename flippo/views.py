from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.views.generic.base import TemplateView

# Create your views here.
from django.shortcuts import redirect
from django.template import loader, RequestContext
from items.helper import fetch_all_info, PriceFetcher, get_flippable
from items.models import Item, MarketInfo


class RegisterView(TemplateView):
    template_name = "register.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['request'] = self.request
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.is_superuser:
            username = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']
            user = User.objects.create_user(username, password, email)

            if user:
                return redirect(reverse_lazy('login') + "?msg=Registered. You can now log in.")
            else:
                return redirect(reverse_lazy('register'))
        else:
            return redirect(reverse_lazy('register') + "?error=Registration is currently disabled.")


class LoginView(TemplateView):
    template_name = "login.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['request'] = self.request
        return context

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse_lazy('index'))
            else:
                return redirect(reverse_lazy('login') + '?error=disabled account')
        else:
            return redirect(reverse_lazy('login') + '?error=Invalid credentials')


def LogoutView(request):
    logout(request)
    return redirect(reverse_lazy('index'))


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