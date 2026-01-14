import os
from gocd_tools.defaults import (
    is_env_set,
    ENV_GO_PLUGIN_DIR,
    GO_PLUGIN_DIR,
    BUNDLED_PLUGIN,
    GOCD_SECRET_PLUGIN,
)


def get_plugin_dir():
    plugin_path, msg = is_env_set(ENV_GO_PLUGIN_DIR)
    if not plugin_path:
        if GO_PLUGIN_DIR:
            return GO_PLUGIN_DIR, ""
        return False, msg
    return plugin_path, ""


def get_plugin_path(plugin_type=BUNDLED_PLUGIN, plugin=GOCD_SECRET_PLUGIN):
    plugin_dir_path, msg = get_plugin_dir()
    if not plugin_dir_path:
        return False, msg
    return os.path.join(plugin_dir_path, plugin_type, plugin), ""
