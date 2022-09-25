import profile
from django.db import models
from datetime import datetime
from .choices import purchase_choices, property_choices
from realtor.models import Realtors
from django.db.models.signals import post_save, pre_save

# Create your models here.


class Listings(models.Model):
    listing_id = models.AutoField(
        verbose_name='ID',
        primary_key=True,
    )
    realtor_id = models.ForeignKey(Realtors, on_delete=models.DO_NOTHING)
    listing_title = models.CharField(
        max_length=100,
        verbose_name='Title',
    )
    state = models.CharField(max_length=100, verbose_name='State')
    district = models.CharField(max_length=100, verbose_name='District')
    city = models.CharField(max_length=100, verbose_name='City')
    description = models.TextField(blank=True, verbose_name='Description')
    price = models.DecimalField(
        verbose_name='Price', max_digits=15, decimal_places=5)
    purchaseType = models.CharField(
        max_length=8, default='Buy', verbose_name='PurchaseType')
    propertyType = models.CharField(
        max_length=15, default='House', verbose_name='PropertyType')
    bedroom = models.IntegerField(
        verbose_name='Bedroom', default=None, blank=True, null=True)
    bathroom = models.IntegerField(
        verbose_name='Bathroom', default=None, blank=True, null=True)
    garage = models.IntegerField(
        verbose_name='Garage', default=None, blank=True, null=True)
    sqft = models.IntegerField(
        verbose_name='Sqft', default=None, blank=True, null=True)
    photo_main = models.ImageField(
        upload_to='photos/%Y/%m/%d/', verbose_name='Main Photo', default=None, blank=True, null=True)
    is_published = models.BooleanField(default=True, verbose_name='Published')
    list_date = models.DateTimeField(
        default=datetime.now, blank=True, verbose_name='List Date')

    class Meta():
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'

    def __str__(self):
        return self.listing_title


class Photos(models.Model):
    listing_id = models.ForeignKey(Listings, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)

    class Meta():
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'


class Scraper(models.Model):
    scraper_id = models.AutoField(
        verbose_name='ID',
        primary_key=True,
        unique=True
    )
    scrapertitle = models.CharField(
        max_length=255,
        verbose_name='ScraperTitle',
        unique=True
    )
    scraper_location = models.CharField(
        max_length=100,
        verbose_name='ScraperLocation',
    )
    scraper_price = models.CharField(
        max_length=100,
        verbose_name='ScraperPrice',
    )

    scraper_image = models.CharField(
        max_length=200,
        verbose_name='ScraperImage', default=None, blank=True, null=True,
        unique=True
    )

    class Meta():
        verbose_name = 'Scraper'
        verbose_name_plural = 'Scrapers'

    def __str__(self):
        return self.scrapertitle
