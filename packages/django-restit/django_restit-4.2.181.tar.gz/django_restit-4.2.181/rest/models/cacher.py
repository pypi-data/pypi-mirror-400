from django.db import models as dm
from rest import fields as rf
from rest import helpers as rh
from objict import objict


class ModelCache(dm.Model):
    class Meta:
        abstract = True

    modified = dm.DateTimeField(auto_now=True, editable=True, db_index=True)

    component = dm.SlugField(max_length=200, null=True, blank=True, default=None, db_index=True)
    component_id = dm.IntegerField(null=True, blank=True, default=None, db_index=True)

    query = dm.CharField(max_length=255, null=True, blank=True, default=None, db_index=True)

    cache = rf.JSONField()

