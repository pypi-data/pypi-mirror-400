from django.utils.translation import gettext_lazy as _
from djangoldp import fields

from djangoldp_ds4go.models.__base_model import baseModel


class baseNamedModel(baseModel):
    name = fields.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Name"),
    )

    def __str__(self):
        return self.name or self.urlid

    class Meta(baseModel.Meta):
        abstract = True
        serializer_fields = baseModel.Meta.serializer_fields + [
            "name",
        ]
