import os
import kmviz.core.config as kconf
from kmviz.core import KmVizError
from kmviz.core.log import setup_logger

from kmviz.init import make_kmviz_app

config_file = os.environ["KMVIZ_CONF"]
log_directory = os.environ["KMVIZ_LOG_DIR"]
log_stderr = os.environ["KMVIZ_LOG_STDERR"]
verbosity = os.environ["KMVIZ_VERBOSITY"]

if not config_file:
    raise KmVizError("'KMVIZ_CONF' env variable not found")

if not log_directory:
    log_directory = ".kmviz_log"

if not verbosity:
    verbosity = "INFO"

if not log_stderr:
    log_stderr = True

kconf.init_global_state()

setup_logger(verbosity, log_directory=log_directory, with_stderr=log_stderr, traceback=None)

kconf.st.configure("db", config_file)
app = make_kmviz_app(kconf.st)
app = app.server






