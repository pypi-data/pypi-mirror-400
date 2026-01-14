from django.utils.translation import gettext_lazy as _
from djangoldp import fields
from djangoldp_i18n.views import I18nLDPViewSet

from djangoldp_ds4go.models.__base_named_model import baseNamedModel
from djangoldp_ds4go.models.category import Category


class Fact(baseNamedModel):
    rss_guid = fields.LDPUrlField(
        blank=True, null=True, verbose_name=_("Related RSS GUID")
    )
    link = fields.LDPUrlField(blank=True, null=True, verbose_name=_("Link"))
    review = fields.JSONField(
        blank=True, null=True, default=dict, verbose_name=_("Review")
    )
    description = fields.TextField(blank=True, null=True, verbose_name=_("Description"))
    content = fields.TextField(blank=True, null=True, verbose_name=_("Content"))
    author = fields.TextField(blank=True, null=True, verbose_name=_("Author"))
    categories = fields.ManyToManyField(
        Category,
        blank=True,
        verbose_name=_("Categories"),
        related_name="facts",
    )
    enclosure = fields.LDPUrlField(blank=True, null=True, verbose_name=_("Enclosure"))

    class Meta(baseNamedModel.Meta):
        verbose_name = _("Fact")
        verbose_name_plural = _("Facts")

        rdf_type = "ds4go:Fact"
        serializer_fields = baseNamedModel.Meta.serializer_fields + [
            "link",
            "description",
            "content",
            "author",
            "categories",
            "enclosure",
            "medias",
            "review",
        ]

        nested_fields = baseNamedModel.Meta.nested_fields + ["medias"]

        view_set = I18nLDPViewSet
