from django.utils.translation import gettext_lazy as _
from djangoldp import fields
from djangoldp.models import Model
from djangoldp.permissions import AuthenticatedOnly, ReadOnly


class baseModel(Model):
    created_at = fields.DateTimeField(
        auto_now_add=True, verbose_name=_("Creation Date")
    )
    updated_at = fields.DateTimeField(
        auto_now=True, verbose_name=_("Update Date")
    )

    def __str__(self):
        return self.urlid

    class Meta(Model.Meta):
        abstract = True
        verbose_name = _("Unknown Object")
        verbose_name_plural = _("Unknown Objects")

        serializer_fields = [
            "@id",
            "created_at",
            "updated_at",
        ]
        nested_fields = []
        rdf_type = "ds4go:BasicObject"
        permission_classes = [AuthenticatedOnly & ReadOnly]
