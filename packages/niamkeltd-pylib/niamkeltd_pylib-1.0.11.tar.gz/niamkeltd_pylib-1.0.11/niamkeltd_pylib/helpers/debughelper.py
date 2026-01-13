import os
import inspect
import traceback

def get_filename() -> str:
    return os.path.basename(inspect.stack()[1][0].f_code.co_filename)

def get_filepath() -> str:
    return inspect.stack()[1][0].f_code.co_filename

def exception_stack_trace() -> str:
    return traceback.format_exc()