from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from .models import JobOffer


@admin.register(JobOffer)
class JobOfferAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'title', 'author')
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    search_fields = ['urlid', 'title', 'author__urlid', 'skills__name', 'description']
    ordering = ['urlid']

