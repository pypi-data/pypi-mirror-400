from rest.decorators import periodic
from taskqueue.models import Task


# run every day at 9am UTC
# @periodic(hour=9)
# def run_background_task(force=False, verbose=False, now=None):
#     # this will call a method in tq.py called run_example using a async task
#     Task.Publish("wiki", "run_example", channel="tq_app_handler")


