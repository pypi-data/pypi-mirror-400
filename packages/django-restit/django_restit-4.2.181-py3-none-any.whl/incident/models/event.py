from django.db import models

from rest import models as rm
from rest.extra import JSONMetaData
from rest import log
from rest import settings
from objict import objict

import metrics

from datetime import datetime, timedelta
from .incident import Incident, INCIDENT_STATE_PENDING
from .rules import Rule

INCIDENT_METRICS = settings.get("INCIDENT_METRICS", False)
INCIDENT_EVENT_METRICS = settings.get("INCIDENT_EVENT_METRICS", False)
INCIDENT_EVENT_GRANULARITY = settings.get("INCIDENT_EVENT_GRANULARITY", "hourly")
EVENT_TO_INCIDENT_LEVEL = settings.get("EVENT_TO_INCIDENT_LEVEL", 4)
EVENT_DETAIL_TEMPLATES = settings.get("EVENT_DETAIL_TEMPLATES", None)
EVENT_META_KEYWORDS = settings.get("EVENT_META_KEYWORDS", [
        "path", "ip", "reporter_ip", "code",
        "reason", "buid", "merchant", "tid",
        "group", "http_user_agent", "user_agent",
        "app_url", "isp", "city", "state", "country",
        "username"
    ])

logger = log.getLogger("incident", filename="incident.log")

"""
very generic
external system can post an event
{
     "description": "Critical Test Event",
     "hostname": "r1",
     "details": "A critical event occurred on r1 running blah blah",
     "level": 7,
     "category": "prepaid.event",
     "metadata": {
        "error_stack": "....."
     }
}
"""


class Event(JSONMetaData, rm.RestModel):
    class RestMeta:
        POST_SAVE_FIELDS = ["level", "catagory"]
        SEARCH_FIELDS = ["description", "hostname"]
        VIEW_PERMS = ["view_incidents", "view_logs"]
        CREATE_PERMS = None  # allow anyone to create an event
        GRAPHS = {
            "default": {
                "graphs": {
                    "group": "basic",
                    "created_by": "basic"
                },
            },
            "detailed": {
                "graphs": {
                    "group": "basic",
                    "created_by": "basic",
                    "generic__component": "basic",
                },
            },
        }

    created = models.DateTimeField(auto_now_add=True)
    reporter_ip = models.CharField(max_length=16, blank=True, null=True, default=None, db_index=True)

    hostname = models.CharField(max_length=255, blank=True, null=True, default=None, db_index=True)
    description = models.CharField(max_length=84)
    details = models.TextField(default=None, null=True)

    level = models.IntegerField(default=0, db_index=True)
    category = models.CharField(max_length=124, db_index=True)
    # code = models.IntegerField(default=0, db_index=True)

    group = models.ForeignKey(
        "account.Group", on_delete=models.SET_NULL,
        related_name="+", null=True, default=None)

    component = models.SlugField(max_length=250, null=True, blank=True, default=None)
    component_id = models.IntegerField(null=True, blank=True, default=None)

    # this allows us to bundle multiple events to an incident
    incident = models.ForeignKey(
        Incident, null=True, default=None,
        related_name="events", on_delete=models.SET_NULL)

    def runRules(self):
        for rule in Rule.objects.filter(category=self.category).order_by("priority"):
            if rule.run(self):
                return rule
        return None

    @property
    def details_by_category(self):
        # returns detailed text based on the category settings
        # if EVENT_DETAIL_TEMPLATES is None or self.category not in EVENT_DETAIL_TEMPLATES:
        #     return self.details
        output = []
        if self.component:
            output.append(f"{self.component}({self.component_id})")
        for key in EVENT_META_KEYWORDS:
            if self.metadata.get(key, None) is not None:
                output.append(f"{key}: {self.metadata[key]}")
        if self.details:
            output.append(self.details)
            output.append("")
            output.append("")
        return "\n".join(output)

    def lookupIP(self, ip):
        GeoIP = rm.RestModel.getModel("location", "GeoIP")
        gip = GeoIP.lookup(ip)
        self.setProperty("ip", ip)
        if gip:
            self.setProperty("country", gip.country)
            self.setProperty("state", gip.state)
            self.setProperty("city", gip.city)
            self.setProperty("isp", gip.isp)

    def set_description(self, value):
        # trun desc to 84
        if value is None:
            value = ""
        if len(value) > 84:
            value = value[:80] + "..."
        self.description = value


    def on_rest_created(self, request):
        # Record metrics if enabled
        if INCIDENT_EVENT_METRICS:
            self._record_event_metrics()

        self._update_properties(request)
        # Process rules and create incident if needed
        hit_rule = self.runRules()
        incident = self._process_rules_and_create_incident(hit_rule)

        if incident is None:
            # No incident needed based on rules
            return

        # Update incident metadata
        self.incident = incident
        self.save()

        # Record incident metrics if enabled
        if INCIDENT_METRICS:
            self._record_incident_metrics()

        # Trigger any incident actions
        try:
            incident.triggerAction()
        except Exception:
            logger.exception()

    def _update_properties(self, request):
        # make sure hostname is set
        if self.hostname is None:
            self.hostname = settings.HOSTNAME

        # Update properties
        self.setProperty("level", self.level)
        self.setProperty("category", self.category)
        if not self.getProperty("hostname", None):
            self.setProperty("hostname", self.hostname)

        # lookup IP
        if request and request.DATA.get("ip_lookup", field_type=bool):
            self.reporter_ip = request.ip
            self.lookupIP(request.ip)

    def _record_event_metrics(self):
        """Record event metrics"""
        if self.hostname:
            metrics.metric(
                f"incident_evt_{self.hostname}",
                category="incident_events",
                min_granularity="hourly"
            )
        metrics.metric(
            "incident_evt",
            min_granularity=INCIDENT_EVENT_GRANULARITY
        )

    def _record_incident_metrics(self):
        """Record incident metrics"""
        if self.hostname:
            metrics.metric(
                f"incidents_{self.hostname}",
                category="incidents",
                min_granularity="hourly"
            )
        metrics.metric(
            "incidents",
            min_granularity=INCIDENT_EVENT_GRANULARITY
        )

    def _process_rules_and_create_incident(self, hit_rule):
        """Process rules and create incident if needed"""
        if hit_rule is not None:
            # Handle rule matches
            if hit_rule.action == "ignore":
                self.save()
                return None

            if hit_rule.bundle > 0:
                return Incident.getBundled(rule=hit_rule, event=self)

        elif self.level >= EVENT_TO_INCIDENT_LEVEL:
            # Ignore high levels without rules
            self.save()
            return None

        # Create new incident
        return self._create_incident(hit_rule)

    def _create_incident(self, hit_rule):
        """Create a new incident"""
        incident = Incident(
            rule=hit_rule,
            priority=hit_rule.priority if hit_rule else 10,
            reporter_ip=self.reporter_ip,
            category=self.category,
            group=self.group,
            component=self.component,
            component_id=self.component_id,
            hostname=self.hostname
        )

        # Set incident group from rule if needed
        if self.group is None and hit_rule is not None:
            incident.group = hit_rule.group

        # Set pending state if rule requires
        if hit_rule is not None and hit_rule.action_after != 0:
            incident.state = INCIDENT_STATE_PENDING

        # Set description based on rules and category
        self._set_incident_description(incident, hit_rule)

        incident.save()
        incident.updateMeta(self)
        return incident

    def _set_incident_description(self, incident, hit_rule):
        """Set the incident description"""
        if hit_rule and hit_rule.title_template and "{" in hit_rule.title_template:
            try:
                incident.description = hit_rule.title_template.format(event=self)
            except Exception:
                logger.exception(hit_rule.title_template)
                incident.description = self.description
        elif self.category == "ossec":
            incident.description = f"{self.hostname}: {self.description}"
            incident.save()
            incident.updateAbuseInfo()
        else:
            incident.description = self.description
