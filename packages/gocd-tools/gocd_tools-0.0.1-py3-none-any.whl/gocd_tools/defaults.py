import os
from gocd_tools.utils import is_env_set

PACKAGE_NAME = "gocd-tools"

# API Request Defaults
CONTENT_TYPE = "application/json"
JSON_HEADER = {"Content-Type": CONTENT_TYPE}

API_VERSION_1 = "application/vnd.go.cd.v1+json"
API_VERSION_2 = "application/vnd.go.cd.v2+json"
API_VERSION_3 = "application/vnd.go.cd.v3+json"
API_VERSION_4 = "application/vnd.go.cd.v4+json"
API_VERSION_7 = "application/vnd.go.cd.v7+json"

ACCEPT_HEADER_1 = {"Accept": API_VERSION_1, **JSON_HEADER}
ACCEPT_HEADER_2 = {"Accept": API_VERSION_2, **JSON_HEADER}
ACCEPT_HEADER_3 = {"Accept": API_VERSION_3, **JSON_HEADER}
ACCEPT_HEADER_4 = {"Accept": API_VERSION_4, **JSON_HEADER}
ACCEPT_HEADER_7 = {"Accept": API_VERSION_7, **JSON_HEADER}

GITHUB_API_VERSION = "application/vnd.github.v3+json"
GITHUB_ACCEPT_HEADER = {"Accept": GITHUB_API_VERSION}

# API default endpoints
if "GOCD_BASE_URL" in os.environ:
    GOCD_BASE_URL = os.environ["GOCD_BASE_URL"]

if GOCD_BASE_URL == "":
    print(
        "The require environment variable GOCD_BASE_URL was empty: {}".format(
            GOCD_BASE_URL
        )
    )
    exit(1)

# Github URLs
GITHUB_AUTH_URL = "https://api.github.com/user"
GITHUB_GOCD_AUTH_URL = ""

# Public URLs
GO_URL = "{}/go".format(GOCD_BASE_URL)
API_URL = "{}/api".format(GO_URL)
AUTH_URL = "{}/current_user".format(API_URL)
ELASTIC_AGENT_URL = "{}/elastic/profiles".format(API_URL)
ADMIN_URL = "{}/admin".format(API_URL)
SECURITY_URL = "{}/security".format(ADMIN_URL)
ROLE_URL = "{}/roles".format(SECURITY_URL)

# Restricted URLs
AUTHORIZATION_CONFIG_URL = "{}/auth_configs".format(SECURITY_URL)
CLUSTER_PROFILES_URL = "{}/elastic/cluster_profiles".format(ADMIN_URL)
PIPELINE_GROUPS_URL = "{}/pipeline_groups".format(ADMIN_URL)
CONFIG_REPO_URL = "{}/config_repos".format(ADMIN_URL)
TEMPLATE_URL = "{}/templates".format(ADMIN_URL)
SECRET_CONFIG_URL = "{}/secret_configs".format(ADMIN_URL)

# Server config
CONFIG_SERVER = "{}/config/server".format(ADMIN_URL)
ARTIFACT_CONFIG = "{}/artifact_config".format(CONFIG_SERVER)

if "GOCD_AUTH_TOKEN" in os.environ:
    GOCD_AUTH_TOKEN = os.environ["GOCD_AUTH_TOKEN"]
    # The GOCD_AUTH_TOKEN is the one generate within the GOCD server
    # (Not GitHub)
else:
    GOCD_AUTH_TOKEN = ""

if "GITHUB_AUTH_TOKEN" in os.environ:
    GITHUB_AUTH_TOKEN = os.environ["GITHUB_AUTH_TOKEN"]
else:
    GITHUB_AUTH_TOKEN = ""


AUTHORIZATION_HEADER = {
    "Authorization": "bearer {}".format(GOCD_AUTH_TOKEN),
    **ACCEPT_HEADER_1,
}

GITHUB_AUTHORIZATION_HEADER = {
    "Authorization": "token {}".format(GITHUB_AUTH_TOKEN),
    **GITHUB_ACCEPT_HEADER,
}

# Server defaults
GO_DATA_DIR = "/godata"
GO_SECRET_DIR = "/gosecret"
GO_SECRET_DB_FILE = "secrets.yml"
GO_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".{}".format(PACKAGE_NAME))
GO_PLUGIN_DIR = os.path.join(GO_DATA_DIR, "plugins")

# Other constants
GOCD_SECRET_PLUGIN = "gocd-file-based-secrets-plugin.jar"

BUNDLED_PLUGIN = "bundled"
EXTERNAL_PLUGIN = "external"

# Environment variables
ENV_GO_DATA_DIR = "GO_DATA_DIR"
ENV_GO_SECRET_DIR = "GO_SECRET_DIR"
ENV_GO_SECRET_DB_FILE = "GO_SECRET_DB_FILE"
ENV_GO_CONFIG_DIR = "GO_CONFIG_DIR"
ENV_GO_PLUGIN_DIR = "GO_PLUGIN_DIR"

# Default configuration input paths
default_base_path = GO_CONFIG_DIR
default_config_path = os.path.join(default_base_path, "config")

artifacts_config_path = os.path.join(default_config_path, "artifacts_config.yml")
authorization_config_path = os.path.join(
    default_config_path, "authorization_configuration.yml"
)
cluster_profiles_path = os.path.join(default_config_path, "cluster_profiles.yml")
config_repositories_path = os.path.join(default_config_path, "config_repositories.yml")
elastic_agent_profile_path = os.path.join(
    default_config_path, "elastic_agent_profiles.yml"
)
pipeline_group_configs_path = os.path.join(
    default_config_path, "pipeline_group_configs.yml"
)
roles_path = os.path.join(default_config_path, "roles.yml")
secret_configs_path = os.path.join(default_config_path, "secret_configs.yml")
templates_path = os.path.join(default_config_path, "templates.yml")


# Datadir discover
def get_data_dir():
    data_path, msg = is_env_set(ENV_GO_DATA_DIR)
    if not data_path:
        if GO_DATA_DIR:
            return GO_DATA_DIR, ""
        return False, msg
    return data_path, ""


# Secrets discover
def get_secrets_dir_path():
    env_dir_path, msg = is_env_set(ENV_GO_SECRET_DIR)
    if not env_dir_path:
        # Use the default as a backup
        if GO_SECRET_DIR:
            return GO_SECRET_DIR, ""
        return False, msg
    return env_dir_path, ""


def get_secrets_file_name():
    secrets_name, msg = is_env_set(ENV_GO_SECRET_DB_FILE)
    if not secrets_name:
        # Use the default as a backup
        if GO_SECRET_DB_FILE:
            return GO_SECRET_DB_FILE, ""
        return False, msg
    return secrets_name, ""


def get_secrets_db_path():
    dir_path, msg = get_secrets_dir_path()
    if not dir_path:
        return False, msg
    file_name, msg = get_secrets_file_name()
    if not file_name:
        return False, msg
    return os.path.join(dir_path, file_name), ""
