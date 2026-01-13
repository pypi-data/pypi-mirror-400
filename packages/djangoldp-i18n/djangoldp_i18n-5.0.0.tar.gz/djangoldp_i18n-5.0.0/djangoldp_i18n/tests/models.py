from django.db import models
from djangoldp.models import Model
from djangoldp_i18n.views import I18nLDPViewSet


class MultiLingualModel(Model):
    title = models.CharField(max_length=255, blank=True, null=True)

    class Meta(Model.Meta):
        ordering = ['pk']
        depth = 1
        view_set = I18nLDPViewSet


class MultiLingualChild(Model):
    parent = models.ForeignKey(MultiLingualModel, on_delete=models.CASCADE, related_name='children')
    title = models.CharField(max_length=255, blank=True, null=True)

    class Meta(Model.Meta):
        ordering = ['pk']
        view_set = I18nLDPViewSet
