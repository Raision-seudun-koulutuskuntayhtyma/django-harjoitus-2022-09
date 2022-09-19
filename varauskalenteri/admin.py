from django.contrib import admin

from .models import Tapahtuma


@admin.register(Tapahtuma)
class TapahtumaAdmin(admin.ModelAdmin):
    pass
