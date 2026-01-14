from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from djangoldp_i18n.admin import DjangoLDPI18nAdmin

from djangoldp_ds4go.models import *


@admin.register(
    Category,
    Media,
)
class DS4GOModelAdmin(DjangoLDPI18nAdmin, DjangoLDPAdmin):
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    exclude = ("is_backlink", "allow_create_backlink")


class MediaInline(admin.TabularInline):
    model = Media
    extra = 1
    fields = (
        "url",
        "file_size",
        "width",
        "height",
        "file_type",
        "description",
    )


@admin.register(Fact)
class FactAdmin(DS4GOModelAdmin):
    inlines = [MediaInline]
