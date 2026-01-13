
import os
import sys

from blackfire_conprof import log

logger = log.get_logger("blackfire_conprof.sitecustomize")

# Ensure other sitecustomize.py is called if available in sys.path
bootstrap_dir = os.path.dirname(__file__)
if bootstrap_dir in sys.path:
    index = sys.path.index(bootstrap_dir)
    del sys.path[index]

    # hold a reference
    ref_sitecustomize = sys.modules["sitecustomize"]
    del sys.modules["sitecustomize"]
    try:
        import sitecustomize
    except ImportError:
        sys.modules["sitecustomize"] = ref_sitecustomize
    else:
        logger.debug("sitecustomize from user found in: %s", sys.path)
    finally:
        # reinsert the bootstrap_dir again
        sys.path.insert(index, bootstrap_dir)

# enable the profiler
try:
    from blackfire_conprof.profiler import Profiler

    # application_name will be auto-populated via PLATFORM_APPLICATION_NAME/BLACKFIRE_CONPROF_APP_NAME
    # profiler.stop() will be called on app exit by default
    profiler = Profiler()
    profiler.start()
except Exception as e:
    logger.warning(e)

