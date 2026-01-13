from django.apps import AppConfig


class DjangoLDPI18nTestsAppConfig(AppConfig):
    name = 'djangoldp_i18n.tests'
    label = 'i18n_tests'

    def ready(self):
        self.set_up_djangoldp_test_models_with_i18n()

    def set_up_djangoldp_test_models_with_i18n(self):
        from djangoldp.models import Model
        from djangoldp_i18n.views import I18nLDPViewSet

        for cls in Model.__subclasses__():
            if hasattr(cls, 'Meta'):
                setattr(cls.Meta, 'view_set', I18nLDPViewSet)
            else:
                setattr(cls._meta, 'view_set', I18nLDPViewSet)
