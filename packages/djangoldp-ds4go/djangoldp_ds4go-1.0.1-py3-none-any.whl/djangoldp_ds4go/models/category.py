from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp import fields
from djangoldp_i18n.views import I18nLDPViewSet

from djangoldp_ds4go.models.__base_named_model import baseNamedModel


class Category(baseNamedModel):
    parent_category = fields.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta(baseNamedModel.Meta):
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        container_path = "categories"

        rdf_type = "ds4go:Category"
        serializer_fields = baseNamedModel.Meta.serializer_fields + [
            "parent_category",
        ]

        view_set = I18nLDPViewSet
