
from ast import For
from cgitb import text
from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .models import Listings, Photos, Scraper
from contact.models import Contact
from .choices import bedroom_choices, price_choices, state_choices, purchase_choices, property_choices
from contact.forms import InquiryModelForm
from django.contrib import messages
from bs4 import BeautifulSoup
from celery import shared_task
from django.core.mail import send_mail
import requests
import re
from django.contrib.auth.decorators import permission_required
# Create your views here.


def index(request):
    title = 'Real Estate Hunt Nepal | Listing'
    template = 'listing/index.html'

    # Order & Filter the context for the listing page.
    listings = Listings.objects.all().order_by(
        '-list_date').filter(is_published=True)

    paginator = Paginator(listings, 6)
    page = request.GET.get('page')
    paged_listings = paginator.get_page(page)

    context = {'title': title,
               'listings': paged_listings,
               }
    return render(request, template, context)


def detail(request, listing_id):
    title = 'Listing | Details'
    template_name = 'listing/detail.html'
    details = get_object_or_404(Listings, pk=listing_id)
    photos = Photos.objects.all().filter(listing_id=listing_id)
    if request.user.is_active:
        inquiry_form = InquiryModelForm(initial={
            'listing_id': listing_id,
            'listing_title': getattr(details, 'listing_title'),
            'contact_name': request.user.first_name + ' ' + request.user.last_name,
            'contact_mail': request.user.email,
            'user_id': request.user.id,
        })

    if request.user.is_anonymous:
        inquiry_form = InquiryModelForm(initial={
            'listing_id': listing_id,
            'listing_title': getattr(details, 'listing_title'),
        })

    context = {
        'title': title,
        'details': details,
        'photos': photos,
        'inquiry_form': inquiry_form,
    }
    return render(request, template_name, context)


def search(request):
    title = 'Search Result'
    template = 'listing/search.html'

    queryset_list = Listings.objects.order_by('-list_date')
    # Keywords
    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            queryset_list = queryset_list.filter(
                description__icontains=keywords)
    # City
    if 'city' in request.GET:
        city = request.GET['city']
        if city:
            queryset_list = queryset_list.filter(
                city__iexact=city)
    # State
    if 'state' in request.GET:
        state = request.GET['state']
        if state:
            queryset_list = queryset_list.filter(
                state__iexact=state)
    # PurchaseType
    if 'purchaseType' in request.GET:
        purchaseType = request.GET['purchaseType']
        if purchaseType:
            queryset_list = queryset_list.filter(
                purchaseType__iexact=purchaseType)

     # PropertyType
    if 'propertyType' in request.GET:
        propertyType = request.GET['propertyType']
        if propertyType:
            queryset_list = queryset_list.filter(
                propertyType__iexact=propertyType)
    # Price
    if 'price' in request.GET:
        price = request.GET['price']
        if price:
            queryset_list = queryset_list.filter(
                price__lte=price)
    context = {'title': title,
               'listings': queryset_list,
               'state_choices': state_choices,
               'purchase_choices': purchase_choices,
               'property_choices': property_choices,
               'price_choices': price_choices,
               }
    return render(request, template, context)


def advanceSearch(request):
    title = 'Advance Search'
    template_name = 'listing/advanceSearch.html'
    scraper = Scraper.objects.all().order_by('scrapertitle')
    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            scraper = scraper.filter(
                scrapertitle__icontains=keywords)
    # City
    if 'location' in request.GET:
        location = request.GET['location']
        if location:
            scraper = scraper.filter(
                scraper_location__iexact=location)
    # Price
    if 'price' in request.GET:
        price = request.GET['price']
        if price:
            scraper = scraper.filter(
                scraper_price__lte=price)

    context = {
        'title': title,
        'scraper': scraper,
        'price_choices': price_choices
    }
    return render(request, template_name, context)


def scraperDetail(request, scraper_id):
    title = 'Scraper | Details'
    template_name = 'listing/scraperDetails.html'
    obj = get_object_or_404(Scraper, pk=scraper_id)
    if request.user.is_active:
        inquiry_form = InquiryModelForm(initial={
            'listing_id': scraper_id,
            'listing_title': getattr(obj, 'scrapertitle'),
            'contact_name': request.user.first_name + ' ' + request.user.last_name,
            'contact_mail': request.user.email,
            'user_id': request.user.id,
        })

    if request.user.is_anonymous:
        inquiry_form = InquiryModelForm(initial={
            'listing_id': scraper_id,
            'listing_title': getattr(obj, 'scrapertitle'),
        })
    context = {
        'title': title,
        'obj': obj,
        'inquiry_form': inquiry_form,
    }
    return render(request, template_name, context)


@permission_required('admin.can_add_log_entry')
@shared_task
def csv_upload(request):
    template = 'listing/uploadCsv.html'

    if request.method == 'POST':
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
        r = requests.get(
            'https://www.realestateinnepal.com/search/?location=', headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        con = get_object_or_404(Contact)
        subject = 'Real Estate Hunt Nepal Notification'
        message = 'The price of the properties on Advance have been updated. Please check out our latest prices. '
        from_email = 'REAL ESTATE HUNT NEPAL'
        to_email = con.contact_mail
        send_mail(
            subject,
            message,
            from_email,
            [to_email]
        )
        lists = soup.find_all(
            'div', class_="shadow border-bottom border-primary mb-4")
        for list in lists:
            title = list.find(
                'a', class_="text-white").text.replace('\n', '')
            location = list.find(
                'span', class_="locationko text-white").text.split()[-1].replace('\n', '')
            priceOne = list.find(
                'div', class_="bg-white p-3").text.split()[+9].replace('\n', '')
            image = list.find(
                'img')['src']
            price = re.sub('[^0-9]', '', priceOne)
            _, created = Scraper.objects.update_or_create(
                scrapertitle=title,
                scraper_location=location,
                scraper_price=price,
                scraper_image=image
            )

    context = {}
    return render(request, template, context)


@shared_task
def notify(request):
    template = 'listing/uploadCsv.html'
    con = get_object_or_404(Contact)
    subject = 'Real Estate Hunt Nepal Notification'
    message = 'Your submission on the property of message('+con.contact_message + \
        ') has been submitted sucessfully. You will be notified about this property.'
    from_email = 'REAL ESTATE HUNT NEPAL'
    to_email = con.contact_mail
    send_mail(
        subject,
        message,
        from_email,
        [to_email]
    )

    context = {}
    return render(request, template, context)
