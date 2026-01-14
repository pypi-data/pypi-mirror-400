from rest import helpers as rh
from rest.log import getLogger
import time


def run_example(task):
    # a background task has been pushed to this call
    logger = getLogger("wiki", "wiki.log")
    task.log("starting task")
    time.sleep(10)
    task.log("finished my task")
    logger.info("task completed")


