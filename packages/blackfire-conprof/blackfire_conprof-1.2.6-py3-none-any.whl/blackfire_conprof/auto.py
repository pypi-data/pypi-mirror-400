import os

# there is a code path in ddtrace.auto that reads this env var
# and starts the profiler. We need to remove it to avoid starting a second profiler
dd_profiling_enabled_value = os.environ.get("DD_PROFILING_ENABLED")
dd_trace_enabled_value = os.environ.get("DD_TRACE_ENABLED")
if dd_profiling_enabled_value:
    del os.environ['DD_PROFILING_ENABLED']
if dd_trace_enabled_value:
    del os.environ['DD_TRACE_ENABLED']

# # DD profiler requires this for patching the runtime. Example: for gevent to work
# # correctly, this needs to be imported before gevent.patch_all()
import ddtrace.auto

if dd_profiling_enabled_value:
    os.environ['DD_PROFILING_ENABLED'] = dd_profiling_enabled_value
if dd_trace_enabled_value:
    os.environ['DD_TRACE_ENABLED'] = dd_trace_enabled_value
