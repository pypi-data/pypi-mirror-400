from modeltranslation.translator import TranslationOptions, register

from djangoldp_ds4go.models import Category, Fact, Media


@register(Fact)
class FactTranslationOptions(TranslationOptions):
    fields = ("name", "description", "content", "author", "enclosure")


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Media)
class MediaTranslationOptions(TranslationOptions):
    fields = ("description",)
