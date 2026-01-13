import re
import os
import platform
import collections
from blackfire_conprof import log
from .version import __version__

_DEFAULT_PERIOD = 45 # secs
_DEFAULT_UPLOAD_TIMEOUT = 10 # secs

def _get_default_agent_socket():
    plat = platform.system()
    if plat == 'Windows':
        return 'tcp://127.0.0.1:8307'
    elif plat == 'Darwin':
        if platform.processor() == 'arm':
            return 'unix:///opt/homebrew/var/run/blackfire-agent.sock'
        else:
            return 'unix:///usr/local/var/run/blackfire-agent.sock'
    else:
        return 'unix:///var/run/blackfire/agent.sock'


def parse_network_address_string(agent_socket):
    pattern = re.compile(r'^([^:]+)://(.*)')
    matches = pattern.findall(agent_socket)
    if not matches:
        return None, None
    network, address = matches[0]
    return network, address

_CustomLabel = collections.namedtuple("_CustomLabel", ["name", "env_var"])
_blackfire_labels = [
    _CustomLabel(name="project_id", env_var="PLATFORM_PROJECT"),
]

class Profiler(object):

    def __init__(self, application_name=None, agent_socket=None, 
                 server_id='', server_token='', period=_DEFAULT_PERIOD, 
                 upload_timeout=_DEFAULT_UPLOAD_TIMEOUT, labels={}):
        agent_socket = agent_socket or os.environ.get(
            'BLACKFIRE_AGENT_SOCKET', _get_default_agent_socket()
        )

        network, address = parse_network_address_string(agent_socket)
        if network is None or address is None:
            raise ValueError(
                "Could not parse agent socket value: [%s]" % agent_socket
            )
        if network == "tcp":
            agent_socket = "http://%s" % (address)

        if application_name is None:
            application_name = os.environ.get(
                "BLACKFIRE_CONPROF_APP_NAME") or os.environ.get(
                "PLATFORM_APPLICATION_NAME")

        for label in _blackfire_labels:
            # don't override if user defined
            if label in labels:
                continue

            env_value = os.environ.get(label.env_var)
            if env_value:
                labels[label.name] = env_value

        # init default labels
        # runtime, language and runtime_version are already set by DD
        labels["runtime_os"] = platform.system()
        labels["runtime_arch"] = platform.machine()
        labels["probe_version"] = __version__
       
        # init DD profiler config via. env vars where Profiler object does not 
        # provide a way to set them
        os.environ["DD_PROFILING_UPLOAD_INTERVAL"] = str(period)
        os.environ["DD_PROFILING_API_TIMEOUT"] = str(upload_timeout)
        os.environ["DD_INSTRUMENTATION_TELEMETRY_ENABLED"] = "False"
        os.environ["DD_TRACE_AGENT_URL"] = agent_socket

        api_key = ''
        if server_id and server_token:
            api_key = '%s:%s' % (server_id, server_token)

        # if application_name(service) is still None here, DD fills with the 
        # current running module name
        from ddtrace.profiling import Profiler as DDProfiler
        self._profiler = DDProfiler(
            service=application_name,
            tags=labels,
            api_key=api_key,
            enable_code_provenance=False,
        )

        # needs to be done after DDProfiler import
        log.bridge_ddtrace_logging()

        self.logger = log.get_logger(__name__)

    def start(self, *args, **kwargs):
        self._profiler.start(*args, **kwargs)

        self.logger.info("Started profiling")

    def stop(self):
        self._profiler.stop()

        self.logger.info("Profiling stopped")
