from django.db import models
from django.conf import settings

from rest import models as rm
from rest import helpers as rh


class Ticket(models.Model, rm.RestModel, rm.MetaDataModel):
    class RestMeta:
        SEARCH_FIELDS = ["title", "description"]
        CAN_DELETE = True
        VIEW_PERMS = ["view_tickets"]
        GRAPHS = {
            "default": {
                "extra": ["metadata"],
                "graphs": {
                    "group": "basic",
                    "created_by": "basic",
                    "assigned_to": "basic",
                    "incident": "basic"
                },
            },
            "detailed": {
                "graphs": {
                    "group": "basic",
                    "created_by": "basic",
                    "assigned_to": "basic",
                    "incident": "basic",
                    "generic__component": "basic"
                },
            },
        }

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    group = models.ForeignKey(
        "account.Group", on_delete=models.SET_NULL, 
        related_name="tickets",
        null=True, default=None)
    assigned_to = models.ForeignKey(
        "account.Member", on_delete=models.SET_NULL, 
        related_name="tickets",
        null=True, default=None)
    created_by = models.ForeignKey(
        "account.Member", on_delete=models.CASCADE,
        related_name="+",
        null=True, default=None)

    # if category is null then this will run on all events?
    category = models.CharField(max_length=200, db_index=True)
    priority = models.IntegerField(default=10, db_index=True)  # 1-10, 1 being the highest

    title = models.CharField(max_length=200)
    description = models.TextField()

    status = models.CharField(max_length=32, default=None, null=True, db_index=True)
    state = models.IntegerField(default=0)  # how many incidents before firing action

    incident = models.ForeignKey(
        "incident.Incident", null=True, default=None, 
        related_name="tickets", on_delete=models.SET_NULL)

    component = models.CharField(max_length=200, null=True, default=None, db_index=True)
    component_id = models.IntegerField(null=True, blank=True, default=None, db_index=True)
