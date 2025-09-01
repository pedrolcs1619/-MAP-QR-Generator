from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "birth_date",)
    search_fields = ("name", "email", "birth_date",)
    list_filter = ("name", "email", "birth_date",)
