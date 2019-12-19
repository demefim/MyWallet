from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _

from MyWallet import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']



@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('account_type',)
    search_fields = ['name']


class SplitInline(admin.TabularInline):
    model = models.Split
    extra = 0


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    inlines = [SplitInline]
    date_hierarchy = 'date'
    search_fields = ['title', 'notes', 'splits__title']
