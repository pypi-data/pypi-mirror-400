from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp import fields
from djangoldp_i18n.views import I18nLDPViewSet

from djangoldp_ds4go.models.__base_model import baseModel
from djangoldp_ds4go.models.fact import Fact


class Media(baseModel):
    url = fields.LDPUrlField(blank=True, null=True, verbose_name=_("URL"))
    file_size = fields.IntegerField(blank=True, null=True, verbose_name=_("File Size"))
    width = fields.IntegerField(blank=True, null=True, verbose_name=_("Width"))
    height = fields.IntegerField(blank=True, null=True, verbose_name=_("Height"))
    file_type = fields.TextField(blank=True, null=True, verbose_name=_("Type"))
    description = fields.TextField(blank=True, null=True, verbose_name=_("Description"))
    related_fact = fields.ForeignKey(
        Fact,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Related Fact"),
        related_name="medias",
    )

    def __str__(self):
        return self.url or self.urlid

    class Meta(baseModel.Meta):
        verbose_name = _("Media")
        verbose_name_plural = _("Medias")

        rdf_type = "ds4go:Media"
        serializer_fields = baseModel.Meta.serializer_fields + [
            "url",
            "file_size",
            "width",
            "height",
            "file_type",
            "description",
        ]

        view_set = I18nLDPViewSet
