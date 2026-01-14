from django.db import models as dm
from rest import models as rm


class PageRevision(dm.Model, rm.RestModel):
    created = dm.DateTimeField(auto_now_add=True, editable=False)

    owner = dm.ForeignKey(
        "account.Member", related_name="+",
        blank=True, null=True, default=None,
        on_delete=dm.SET_NULL)

    group = dm.ForeignKey(
        "account.Group", related_name="+", 
        blank=True, null=True, default=None,
        on_delete=dm.SET_NULL)

    entry = dm.ForeignKey(
        "wiki.Page", related_name="revisions", 
        default=None, null=True, blank=True,
        on_delete=dm.CASCADE)

    title = dm.CharField(max_length=255)
    slug = dm.SlugField()

    body = dm.TextField(blank=True)
