from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model

class TestObject(Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    identifier = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)

    class Meta(Model.Meta):
        indexed_fields = ['title',]
        container_path = "/test-objects/"
        verbose_name = _("Test Object")
        verbose_name_plural = _("Test Objects")
        rdf_type = ["test:Object"] 