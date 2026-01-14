import requests
import json
from gocd_tools.defaults import (
    authorization_config_path,
    artifacts_config_path,
    cluster_profiles_path,
    elastic_agent_profile_path,
    pipeline_group_configs_path,
    config_repositories_path,
    roles_path,
    templates_path,
    secret_configs_path,
    GITHUB_GOCD_AUTH_URL,
    ACCEPT_HEADER_1,
    ACCEPT_HEADER_2,
    ACCEPT_HEADER_3,
    ACCEPT_HEADER_4,
    ACCEPT_HEADER_7,
    GOCD_BASE_URL,
    AUTH_URL,
    AUTHORIZATION_HEADER,
    SECRET_CONFIG_URL,
    AUTHORIZATION_CONFIG_URL,
    CLUSTER_PROFILES_URL,
    ELASTIC_AGENT_URL,
    PIPELINE_GROUPS_URL,
    ROLE_URL,
    CONFIG_REPO_URL,
    ARTIFACT_CONFIG,
    TEMPLATE_URL,
)
from gocd_tools.config import load_config


def head(session, url, *args, **kwargs):
    try:
        return session.head(url, *args, **kwargs)
    except Exception as err:
        print("Failed HEAD request: {}".format(err))
    return None


def get(session, url, *args, **kwargs):
    try:
        return session.get(url, *args, **kwargs)
    except Exception as err:
        print("Failed GET request: {}".format(err))
    return None


def delete(session, url, *args, **kwargs):
    try:
        return session.delete(url, *args, **kwargs)
    except Exception as err:
        print("Failed DELETE request: {}".format(err))
    return None


def post(session, url, *args, **kwargs):
    try:
        return session.post(url, *args, **kwargs)
    except Exception as err:
        print("Failed POST request: {}".format(err))
    return None


def put(session, url, *args, **kwargs):
    try:
        return session.put(url, *args, **kwargs)
    except Exception as err:
        print("Failed PUT request: {}".format(err))
    return None


def get_type(session, base_url, id, headers=None):
    id_url = "{}/{}".format(base_url, id)
    resp = get(session, id_url, headers=headers)
    if resp.status_code == 200:
        return resp.headers, resp.text
    print("Failed to find: {}:{}".format(resp.status_code, resp.text))
    return None, None


def get_types(session, base_url, headers=None):
    resp = get(session, base_url, headers=headers)
    if resp.status_code == 200:
        return resp.headers, resp.text
    print("{}:{}".format(resp.status_code, resp.text))
    return None, None


def create_type(session, url, data=None, headers=None):
    json_data = json.dumps(data)
    created = post(session, url, data=json_data, headers=headers)
    if created.status_code == 200:
        return True
    print("{}:{}".format(created.status_code, created.text))
    return False


def delete_type(session, base_url, id, headers=None):
    id_url = "{}/{}".format(base_url, id)
    created = delete(session, id_url, headers=headers)
    if created.status_code == 200:
        return True
    print("{}:{}".format(created.status_code, created.text))
    return False


def update(session, url, data=None, headers=None):
    json_data = json.dumps(data)
    updated = put(session, url, data=json_data, headers=headers)
    if updated.status_code == 200 or updated.status_code == 201:
        return True
    print("Failed to update type: {}:{}".format(updated.status_code, updated.text))
    return False


def update_type(session, base_url, id, data=None, headers=None):
    id_url = "{}/{}".format(base_url, id)
    return update(session, id_url, data=data, headers=headers)


# def authenticate_github(session):
#     if GOCD_AUTH_TOKEN == "":
#         print(
#             "The required environment variable GOCD_AUTH_TOKEN was empty: {}".format(
#                 GOCD_AUTH_TOKEN
#             )
#         )
#         return False

#     # Login to regular github
#     github_auth = get(session, GITHUB_AUTH_URL, headers=GITHUB_AUTHORIZATION_HEADER)
#     if github_auth.status_code != 200:
#         print(
#             "Failed to authenticate with GitHub: {} - {}".format(
#                 github_auth.status_code, github_auth.text
#             )
#         )
#         return False

#     redirect_location = get(
#         session,
#         GITHUB_GOCD_AUTH_URL,
#         allow_redirects=False,
#         headers=GITHUB_AUTHORIZATION_HEADER,
#     )
#     if not redirect_location.status_code == 302:
#         print(
#             "Failed to get the GitHub auth location: {} - {}".format(
#                 redirect_location.status_code, redirect_location.text
#             )
#         )
#         return False

#     if "location" not in redirect_location.headers:
#         print(
#             "Location not available in the GitHUB auth response: {}".format(
#                 redirect_location.headers
#             )
#         )
#         return False

#     # Get the URL location for the GitHub auth page.
#     # TODO, the location_url does not properly authorize
#     # the session with the existing github authentication.
#     # Potentially lookinto a library option like
#     # https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html
#     # location_url = redirect_location.headers["location"]
#     # github_resp = get(
#     #    session, location_url, allow_redirects=False
#     # )
#     #    if not github_resp.status_code == 200:
#     #        return False
#     #    return True
#     return False


def authenticate(session, **auth_kwargs):
    resp = get(session, AUTH_URL, headers=AUTHORIZATION_HEADER, **auth_kwargs)
    if resp.status_code == 200:
        return True
    print("Failed to authenticate: {} - {}".format(resp.status_code, resp.text))
    return False


def is_auth_repo(repository_config):
    if "authentication" not in repository_config:
        return False
    if "required" not in repository_config["authentication"]:
        return False
    if not repository_config["authentication"]["required"]:
        return False
    return True


def repo_auth_data(repository_config):
    return repository_config["authentication"]


def get_repo_secret(auth_data):
    if "secret" not in auth_data:
        return False
    return auth_data["secret"]


def get_repo_secret_manager(repository_config):
    return repository_config["authentication"]["secret_plugin"]


def get_secret_configs(session, headers=None):
    if not headers:
        headers = ACCEPT_HEADER_3
    return get(session, SECRET_CONFIG_URL)


def get_secret_manager(session, id):
    return get_type(session, SECRET_CONFIG_URL, id, headers=ACCEPT_HEADER_3)


def get_aritifacts_config(session, url, headers):
    resp = get(session, url, headers=headers)
    if resp.status_code == 200:
        return resp.headers, resp.text
    return None, None


def init_server():
    """As the first thing, the server's authorization config
    is defined.
    """
    print("Init server: {}".format(GOCD_BASE_URL))
    authorization_configs = load_config(path=authorization_config_path)

    response = {}
    with requests.Session() as session:
        for auth_config in authorization_configs:
            exists = get_type(
                session,
                AUTHORIZATION_CONFIG_URL,
                auth_config["id"],
                headers=ACCEPT_HEADER_2,
            )
            if not exists:
                created = create_type(
                    session,
                    AUTHORIZATION_CONFIG_URL,
                    data=auth_config,
                    headers=ACCEPT_HEADER_2,
                )
                if not created:
                    response["msg"] = (
                        "Failed to create authorization config: {}".format(auth_config)
                    )
                    return False, response
    response["msg"] = "The Authorization config for: {} was completed".format(
        GOCD_BASE_URL
    )
    return True, response


def update_artifacts_config(session, config, url, headers):
    response = {}
    resp_headers, exists = get_aritifacts_config(session, url, headers)
    if not exists:
        response["msg"] = "Failed to find artifacts config to update"
        return False, response

    update_headers = {"If-Match": resp_headers["ETag"], **headers}
    updated = update(
        session,
        url,
        data=config,
        headers=update_headers,
    )
    if not updated:
        response["msg"] = "Failed to update: {}".format(config)
        return False, response
    return True, response


def setup_config(session, config, url, headers, identifer_variable="id"):
    response = {}
    resp_headers, exists = get_type(
        session,
        url,
        config[identifer_variable],
        headers=headers,
    )
    if not exists:
        print("Creating: {}".format(config[identifer_variable]))
        created = create_type(session, url, data=config, headers=headers)
        if not created:
            response["msg"] = "Failed to create: {}".format(config)
            return False, response
    else:
        update_headers = {"If-Match": resp_headers["ETag"], **headers}
        updated = update_type(
            session,
            url,
            config[identifer_variable],
            data=config,
            headers=update_headers,
        )
        if not updated:
            response["msg"] = "Failed to update: {}".format(config)
            return False, response
    return True, response


def setup_configs(session, configs, url, headers, identifer_variable="id"):
    for config in configs:
        success, response = setup_config(
            session,
            config,
            url,
            headers,
            identifer_variable=identifer_variable,
        )
        if not success:
            return False, response
    return True, {}


def remove_config(session, config, url, headers, identifier_variable="id"):
    response = {}
    resp_headers, exists = get_type(
        session,
        url,
        config[identifier_variable],
        headers=headers,
    )
    if exists:
        print("Removing: {}".format(config[identifier_variable]))
        deleted = delete_type(
            session, url, config[identifier_variable], headers=headers
        )
        if not deleted:
            response["msg"] = "Failed to remove: {}".format(config)
            return False, response
    return True, response


def remove_configs(session, configs, url, headers, identifier_variable="id"):
    for config in configs:
        success, response = remove_config(
            session,
            config,
            url,
            headers,
            identifier_variable=identifier_variable,
        )
        if not success:
            return False, response
    return True, {}


def setup_config_repositories(session, configs, url, headers):
    response = {}
    for repository_config in configs:
        resp_headers, exists = get_type(
            session,
            url,
            repository_config["id"],
            headers=headers,
        )
        if not exists:
            # Check whether a secret auth token is required
            if is_auth_repo(repository_config):
                auth_data = repo_auth_data(repository_config)
                repo_secret_manager = get_repo_secret_manager(repository_config)
                _ = get_repo_secret(auth_data)

                secret_manager = get_secret_manager(session, repo_secret_manager)
                if not secret_manager:
                    print(
                        "Repo: {} tries to use secret manager: {}"
                        " which doesn't exist".format(
                            repository_config["id"], repo_secret_manager
                        )
                    )
                # secret = get_type(session, SECRET_CONFIG_URL)
                # if not secret:
                # created = create_secret(repository_config)
                #    created = create_secret(repository_config)
                #    if not created:
                #        print("Failed to create new secret")
                #    extra_config_kwargs["secret"] = created
            print("Creating: {}".format(repository_config["id"]))
            created = create_type(
                session,
                url,
                data={
                    "id": repository_config["id"],
                    **repository_config["config"],
                },
                headers=headers,
            )
            if not created:
                response["msg"] = "Failed to create repository config: {}".format(
                    created
                )
                return False, response
        else:
            updated = update_type(
                session,
                url,
                repository_config["id"],
                data=repository_config,
                headers=headers,
            )
            if not updated:
                response["msg"] = "Failed to update repository config: {}".format(
                    repository_config
                )
                return False, response
    return True, {}


def configure_server():
    authorization_configs = load_config(path=authorization_config_path)
    roles_configs = load_config(path=roles_path)
    # TODO, load and create the authorization config
    configs = [
        {"path": authorization_config_path, "config": authorization_configs},
        {"path": roles_path, "config": roles_configs},
    ]

    artifacts_config = load_config(path=artifacts_config_path)
    cluster_profiles_configs = load_config(path=cluster_profiles_path)
    secret_configs = load_config(path=secret_configs_path)
    elastic_agent_configs = load_config(path=elastic_agent_profile_path)
    pipeline_group_configs = load_config(path=pipeline_group_configs_path)
    templates_configs = load_config(path=templates_path)
    repositories_configs = load_config(path=config_repositories_path)

    optional_configs = [
        (artifacts_config_path, artifacts_config),
        (cluster_profiles_path, cluster_profiles_configs),
        (secret_configs_path, secret_configs),
        (elastic_agent_profile_path, elastic_agent_configs),
        (pipeline_group_configs_path, pipeline_group_configs),
        (templates_path, templates_configs),
        (config_repositories_path, repositories_configs),
    ]

    for optional_config in optional_configs:
        if optional_config[1]:
            configs.append({"path": optional_config[0], "config": optional_config[1]})

    response = {}

    for config in configs:
        if not config["config"]:
            response["msg"] = "Failed loading: {} - config: {}".format(
                config["path"], config["config"]
            )
            return False, response

    with requests.Session() as session:
        print("Authenticate")
        # github_authed = authenticate_github(session)
        # if not github_authed:
        #    response["msg"] = "Failed to authenticate against: {}".format(
        #        GITHUB_AUTH_URL
        #    )
        #    return False, response
        authed = authenticate(session)
        if not authed:
            response["msg"] = "Failed to authenticate against: {}".format(
                GITHUB_GOCD_AUTH_URL
            )
            return False, response

        print("Setup Roles")
        success, response = setup_configs(
            session,
            roles_configs,
            ROLE_URL,
            ACCEPT_HEADER_3,
            identifer_variable="name",
        )
        if not success:
            return False, response

    with requests.Session() as session:
        print("Re-Authenticate")
        authed = authenticate(session)
        if not authed:
            response["msg"] = "Failed to authenticate against: {}".format(
                GITHUB_GOCD_AUTH_URL
            )
            return False, response

        if artifacts_config:
            print("Setup Artifacts Config")
            success, response = update_artifacts_config(
                session, artifacts_config, ARTIFACT_CONFIG, ACCEPT_HEADER_1
            )
            if not success:
                return False, response

        if secret_configs:
            print("Setup Secret Configs")
            success, response = setup_configs(
                session,
                secret_configs,
                SECRET_CONFIG_URL,
                ACCEPT_HEADER_3,
            )
            if not success:
                return False, response

        if cluster_profiles_configs:
            print("Setup Cluster Profiles")
            success, response = setup_configs(
                session,
                cluster_profiles_configs,
                CLUSTER_PROFILES_URL,
                ACCEPT_HEADER_1,
            )
            if not success:
                return False, response

        if elastic_agent_configs:
            print("Setup Elastic Agent Configs")
            success, response = setup_configs(
                session,
                elastic_agent_configs,
                ELASTIC_AGENT_URL,
                ACCEPT_HEADER_2,
            )
            if not success:
                return False, response

        if pipeline_group_configs:
            print("Setup Pipeline Group Configs")
            success, response = setup_configs(
                session,
                pipeline_group_configs,
                PIPELINE_GROUPS_URL,
                ACCEPT_HEADER_1,
                identifer_variable="name",
            )
            if not success:
                return False, response

        if templates_configs:
            print("Create Template Configs")
            success, response = setup_configs(
                session,
                templates_configs,
                TEMPLATE_URL,
                ACCEPT_HEADER_7,
                identifer_variable="name",
            )
            if not success:
                return False, response

        if repositories_configs:
            print("Create Config Repositories")
            success, response = setup_config_repositories(
                session, repositories_configs, CONFIG_REPO_URL, ACCEPT_HEADER_4
            )

            if not success:
                return False, response

        if "msg" not in response:
            response["msg"] = "Succesfully configured the {} endpoint".format(
                GOCD_BASE_URL
            )
        return True, response

    return None, response


def wipe_server():
    repositories_configs = load_config(path=config_repositories_path)
    templates_configs = load_config(path=templates_path)
    pipeline_group_configs = load_config(path=pipeline_group_configs_path)
    elastic_agent_configs = load_config(path=elastic_agent_profile_path)
    cluster_profiles_configs = load_config(path=cluster_profiles_path)
    secret_configs = load_config(path=secret_configs_path)
    roles_configs = load_config(path=roles_path)

    response = {}
    with requests.Session() as session:
        print("Authenticate")
        authed = authenticate(session)
        if not authed:
            response["msg"] = "Failed to authenticate against: {}".format(
                GITHUB_GOCD_AUTH_URL
            )
            return False, response

        if repositories_configs:
            print("Delete Config Repositories")
            success, response = remove_configs(
                session, repositories_configs, CONFIG_REPO_URL, ACCEPT_HEADER_4
            )
            if not success:
                return False, response

        if templates_configs:
            print("Delete Template Configs")
            success, response = remove_configs(
                session,
                templates_configs,
                TEMPLATE_URL,
                ACCEPT_HEADER_7,
                identifier_variable="name",
            )
            if not success:
                return False, response

        if pipeline_group_configs:
            print("Delete Pipeline Config Groups")
            success, response = remove_configs(
                session,
                pipeline_group_configs,
                PIPELINE_GROUPS_URL,
                ACCEPT_HEADER_1,
                identifier_variable="name",
            )
            if not success:
                return False, response

        if elastic_agent_configs:
            print("Delete Elastic Agent Configs")
            success, response = remove_configs(
                session,
                elastic_agent_configs,
                ELASTIC_AGENT_URL,
                ACCEPT_HEADER_2,
            )
            if not success:
                return False, response

        if cluster_profiles_configs:
            print("Delete Cluster Profiles")
            success, response = remove_configs(
                session,
                cluster_profiles_configs,
                CLUSTER_PROFILES_URL,
                ACCEPT_HEADER_1,
            )
            if not success:
                return False, response

        if secret_configs:
            print("Delete Secret Configs")
            success, response = remove_configs(
                session,
                secret_configs,
                SECRET_CONFIG_URL,
                ACCEPT_HEADER_3,
            )
            if not success:
                return False, response

        if roles_configs:
            print("Delete Roles")
            success, response = remove_configs(
                session,
                roles_configs,
                ROLE_URL,
                ACCEPT_HEADER_3,
                identifier_variable="name",
            )
            if not success:
                return False, response

        if "msg" not in response:
            response["msg"] = "Succesfully finished the cleanup of endpoint: {}".format(
                GOCD_BASE_URL
            )
        return True, response
    return None, response


if __name__ == "__main__":
    init_server()
    configure_server()
    wipe_server()
