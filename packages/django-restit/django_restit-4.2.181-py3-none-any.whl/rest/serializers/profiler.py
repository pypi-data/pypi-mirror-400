from rest import log
import os
from functools import wraps
import time

# from line_profiler import LineProfiler
# profiler = LineProfiler()

logger = log.getLogger("profiler", filename="profiler.log")


# def profile(func):
#     def inner(*args, **kwargs):
#         profiler.add_function(func)
#         profiler.enable_by_count()
#         return func(*args, **kwargs)
#     return inner


# def logStats():
#     # profiler.dump_stats(os.path.join(log.LOG_FOLDER, "profiler.log"))
#     profiler.print_stats(stream=logger.stream)


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logger.info(f'Function {func.__name__} Took {total_time:.4f} seconds')
        # logger.info(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper