from django.conf import settings
from django.utils.translation import activate
from django.utils.translation.trans_real import parse_accept_lang_header
from djangoldp.serializers import LDPSerializer, ContainerSerializer


class I18nMixin:
    with_cache = False

    def _get_server_languages(self):
        '''Auxiliary function returns list of language codes used by the server'''
        return [i[0] for i in getattr(settings, 'MODELTRANSLATION_LANGUAGES',
                                      getattr(settings, 'LANGUAGES', []))]

    def _get_default_language(self):
        '''Auxiliary function defines how a default language is found when an invalid language is passed'''
        return getattr(settings, 'MODELTRANSLATION_DEFAULT_LANGUAGE', 'en') or 'en'

    def _get_language(self, requested_languages=None):
        '''returns the language which should be used in the serializer'''
        if requested_languages is None:
            requested_languages = self.context.get('request').META.get('HTTP_ACCEPT_LANGUAGE', None)
        server_languages = self._get_server_languages()

        if requested_languages is not None:
            languages = [i[0] for i in parse_accept_lang_header(requested_languages)]
            for lang in languages:
                lang = lang.lower()
                if lang in server_languages:
                    return lang

            # try base languages for any locales
            for lang in languages:
                if '-' in lang:
                    lang = lang.split('-')[0]
                    if lang in server_languages:
                        return lang

        return self._get_default_language()

    def _append_language_to_context(self, data, active_language):
        context = data.get("@context")
        language_context = {
            '@language': active_language
        }

        if isinstance(context, list):
            data["@context"] = context + [language_context]
        elif isinstance(context, str):
            data["@context"] = [context, language_context]
        elif isinstance(context, dict):
            data['@context'].update({'@language': active_language})
        else:
            data["@context"] = language_context

        return data

    def to_representation(self, obj):
        active_language = self._get_language()
        activate(active_language)

        data = super().to_representation(obj)
        data = self._append_language_to_context(data, active_language)

        return data

    def get_field_names(self, declared_fields, info):
        '''
        Django Rest Framework method which returns fields to be included when instantiating the serializer
        Overridden to exclude translated copies of fields
        '''
        field_names = super().get_field_names(declared_fields, info)
        model_fields = self.Meta.model._meta.get_fields()

        # remove modeltranslation fields
        for field in model_fields:
            module_tree = getattr(field, '__module__', None)
            parent = module_tree.split('.')[0] if module_tree else None

            if parent == 'modeltranslation':
                trans_field_name = field.name
                if trans_field_name in field_names:
                    field_names.remove(trans_field_name)

        return field_names

class I18nContainerSerializer(I18nMixin, ContainerSerializer):
    pass

class I18nLDPSerializer(I18nMixin, LDPSerializer):
    class Meta:
        list_serializer_class = I18nContainerSerializer
    def to_internal_value(self, data):
        language = self._get_language()
        activate(language)
        return super().to_internal_value(data)

    def handle_value_object(self, value):
        if '@language' in value:
            language = self._get_language(requested_languages=value['@language'])
            activate(language)
        return super().handle_value_object(value)