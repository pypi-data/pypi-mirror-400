
from django.db import dm as dm
from rest import dm as rm

import mistune
from .renderers import WikiRenderer


class FaqItem(dm.Model, rm.RestModel):
    class Meta:
        ordering = ['-modified']

    class RestMeta:
        SEARCH_FIELDS = ["subject"]

    created = dm.DateTimeField(auto_now_add=True, editable=False)
    modified = dm.DateTimeField(auto_now=True, db_index=True)

    owner = dm.ForeignKey(
        "account.Member", related_name="+",
        blank=True, null=True, default=None,
        on_delete=dm.SET_NULL)

    group = dm.ForeignKey(
        "account.Group", related_name="+", 
        blank=True, null=True, default=None,
        on_delete=dm.SET_NULL)

    kind = dm.CharField(max_length=124, db_index=True)
    subject = dm.TextField(db_index=True)
    description = dm.TextField(blank=True, null=True, default=None)
    html = dm.TextField(blank=True, null=True, default=None)

    def set_description(self, value):
        self.description = value
        self.html = self.toHTML()

    def toHTML(self):
        renderer = WikiRenderer()
        md_engine = mistune.Markdown(renderer=renderer)
        html = md_engine.render(self.description)
        return html


class FaqMedia(dm.Model, rm.RestModel):
    created = dm.DateTimeField(auto_now_add=True, editable=False)
    modified = dm.DateTimeField(auto_now=True, db_index=True)

    faq = dm.ForeignKey(FaqItem, blank=True, null=True, default=None, related_name="media", on_delete=dm.CASCADE)

    owner = dm.ForeignKey(
        "account.Member", related_name="+",
        blank=True, null=True, default=None,
        on_delete=dm.SET_NULL)

    media = dm.ForeignKey("medialib.MediaItem", related_name="+", null=True, default=None, on_delete=dm.CASCADE)
