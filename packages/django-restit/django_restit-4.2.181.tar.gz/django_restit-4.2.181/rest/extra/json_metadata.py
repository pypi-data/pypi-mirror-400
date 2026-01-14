from django.db import models as dm
from rest import fields as rf
from rest import helpers as rh
from objict import objict


class JSONMetaData(dm.Model):
    class Meta:
        abstract = True
        
    metadata = rf.JSONField()

    def set_metadata(self, value):
        # override set_metadata to call this for updating metadata vs deleting metadata
        if self.metadata is None:
            self.metadata = objict()
        if isinstance(value, dict):
            value = objict.fromdict(value)
            rh.dictDeepUpdate(self.metadata, value)

    def getProperty(self, key, default=None):
        if self.metadata is None:
            return None
        if not isinstance(self.metadata, objict):
            self.metadata = objict.fromdict(self.metadata)
        return self.metadata.get(key, default)

    def setProperty(self, key, value):
        if self.metadata is None:
            self.metadata = objict()
        if not isinstance(self.metadata, objict):
            self.metadata = objict.fromdict(self.metadata)
        self.metadata.set(key, value)
