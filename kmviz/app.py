import os
import kmviz.core.config as kconf
from kmviz.core import KmVizError
from kmviz.init import make_kmviz_app

config_file = os.environ["KMVIZ_CONF"]
if not config_file:
    raise KmVizError("'KMVIZ_CONF' env variable not found")

kconf.init_global_state()
kconf.st.configure("db", config_file)
app = make_kmviz_app(kconf.st)
app = app.server






