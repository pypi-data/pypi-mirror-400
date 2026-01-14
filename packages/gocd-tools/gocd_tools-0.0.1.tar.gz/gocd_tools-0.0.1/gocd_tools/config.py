import yaml
from gocd_tools.io import exists, load


def load_config(path=None):
    if not config_exists(path):
        return False
    return load(path, handler=yaml, Loader=yaml.FullLoader)


def config_exists(path):
    if not path:
        return False
    return exists(path)
