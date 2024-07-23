import dash

import kmviz.core.config as kconf

def make_instance(plugin):
    if plugin:
        return plugin.instance()

_, plugin = kconf.st.instance_plugin

if plugin:
    dash.register_page(__name__, path="/", name=plugin.name(), title=plugin.name())

layout = make_instance(plugin)
