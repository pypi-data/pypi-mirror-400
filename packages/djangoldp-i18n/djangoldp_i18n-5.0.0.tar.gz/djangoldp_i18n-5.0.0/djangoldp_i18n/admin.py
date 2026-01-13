from djangoldp.admin import DjangoLDPAdmin
from modeltranslation.admin import TranslationAdmin


class DjangoLDPI18nAdmin(DjangoLDPAdmin, TranslationAdmin):
    pass
