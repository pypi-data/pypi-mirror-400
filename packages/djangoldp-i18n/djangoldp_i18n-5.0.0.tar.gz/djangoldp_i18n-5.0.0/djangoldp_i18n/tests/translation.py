from modeltranslation.translator import register, TranslationOptions
from .models import MultiLingualModel, MultiLingualChild


@register(MultiLingualModel)
class MutliLingualTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(MultiLingualChild)
class MultiLingualChildTranslationOptions(TranslationOptions):
    fields = ('title',)
    fallback_languages = {'default': ('fr', 'en')}
