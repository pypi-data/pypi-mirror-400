from datetime import datetime, timedelta
from objict import objict
from account.models import Group
from rest import log
import random

from metrics import eod as em

keys = ["count_total", "count_paid", "count_declined", "amount_cents", "fees_cents"]
slug = "testing.set1"
group = Group.objects.last()
# end of day will be 2:30 Central Time
tz = "US/Central"
eod_hour = 14
eod_minute = 30

# for testing history
start = datetime.now() - timedelta(hours=60)

for i in range(0, 60):
    # this will keep track of running sums
    # each time it is called all the fields will be added to the existing values 
    start = start + timedelta(hours=1)
    data = dict(count_paid=0, count_declined=0, amount_cents=0, fees_cents=0)
    data["count_total"] = 1
    if random.randint(0,10) > 7:
        data["count_paid"] = 1
        data["amount_cents"] = random.randint(5, 300) * 100
        data["fees_cents"] = random.randint(1, 8) * 100
    # when is not needed but for the sake of testing we will pass in a when
    # first lets call without a group to get the all
    em.metric(keys, slug, data, when=start, tz=tz, eod_hour=eod_hour, eod_minute=eod_minute)
    # now we can get these metrics
    log.pp(start, data, em.get_metric(slug, start, tz=tz, eod_hour=eod_hour, eod_minute=eod_minute))
    # next lets call with a group to add group specific
    em.metric(keys, slug, data, when=start, group=group, tz=tz, eod_hour=eod_hour, eod_minute=eod_minute)
    log.pp(
        start, data,
        em.get_metric(slug, start, group=group, tz=tz, eod_hour=eod_hour, eod_minute=eod_minute))



log.pp(em.get_metrics(slug, tz=tz, eod_hour=eod_hour, eod_minute=eod_minute))
