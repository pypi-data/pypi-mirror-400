from django.contrib import admin
from django.contrib.admin import register

from NEMO_user_chemicals.models import ChemicalLocation, ChemicalRequest, UserChemical


@register(UserChemical)
class UserChemicalAdmin(admin.ModelAdmin):
    list_display = ("owner", "label_id", "chemical", "expiration")
    autocomplete_fields = ["owner"]


@register(ChemicalRequest)
class ChemicalRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "requester", "date", "name", "approved")
    filter_horizontal = ["hazards"]


@register(ChemicalLocation)
class ChemicalLocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
