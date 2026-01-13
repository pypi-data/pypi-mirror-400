from django.urls import path
from djangoldp_i18n.tests.models import MultiLingualModel, MultiLingualChild
from djangoldp_i18n.views import I18nLDPViewSet

urlpatterns = [
    path('multilingualmodel/', I18nLDPViewSet.urls(
        model=MultiLingualModel, nested_fields=['children'])),
    path('multilingualchildren/', I18nLDPViewSet.urls(
        model=MultiLingualChild, nested_fields=[])),
]
