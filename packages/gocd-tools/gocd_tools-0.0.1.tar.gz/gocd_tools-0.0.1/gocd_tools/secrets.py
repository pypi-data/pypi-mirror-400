from gocd_tools.defaults import get_secrets_dir_path, get_secrets_db_path
from gocd_tools.config import load_config
from gocd_tools.plugin import get_plugin_path
from gocd_tools.io import exists, makedirs, removedir
from gocd_tools.utils import process, format_output_json


def init_secrets_dir():
    response = {}
    secrets_dir_path, msg = get_secrets_dir_path()
    if not secrets_dir_path:
        response["msg"] = msg
        return False, response

    if not exists(secrets_dir_path):
        # Ensure the secrets dir is there
        created, msg = makedirs(secrets_dir_path)
        response["msg"] = msg
        if not created:
            return False, response
        return True, response

    response["msg"] = "The secrets db directory already exists: {}".format(
        secrets_dir_path
    )
    return True, response


def del_secrets_dir():
    response = {}
    db_path, msg = get_secrets_dir_path()
    if not db_path:
        response["msg"] = msg
        return False, response

    if not exists(db_path):
        response["msg"] = "The db path: {} does not exist".format(db_path)
        return True, response

    removed, msg = removedir(db_path)
    response["msg"] = msg
    if not removed:
        return False, response
    return True, response


def add_secret(add_command, key, value):
    response = {}
    add_secret_cmd = add_command + ["-n", key, "-v", value]
    execute_kwargs = {"commands": [add_secret_cmd], "capture": True}
    results = process(execute_kwargs=execute_kwargs)
    for result in results:
        json_result = format_output_json(result)

        if (
            "status" in json_result["error"]
            and json_result["error"]["status"] == "failed"
        ):
            if "msg" in json_result["error"]:
                response["msg"] = json_result["error"]["msg"]
                return False, response
            else:
                response["msg"] = json_result
                return False, response
    return True, response


def configure_secrets():
    """This function is required to be run on the target
    server because it is using the file secret plugin"""
    response = {}
    secret_db_path, msg = get_secrets_db_path()
    secret_db = load_config(path=secret_db_path)
    if not secret_db:
        response["msg"] = "The secret db at: {} could not be loaded".format(
            secret_db_path
        )
        return False, response

    file_secret_plugin_path, msg = get_plugin_path()
    if not file_secret_plugin_path:
        response["msg"] = msg
        return False, response

    if not exists(file_secret_plugin_path):
        response["msg"] = "The plugin path path: {} does not exist".format(
            file_secret_plugin_path
        )
        return False, response

    # Initialize the secret DBs at the server
    base_plugin_cmd = ["java", "-jar", file_secret_plugin_path]
    create_db_cmd = base_plugin_cmd + ["init", "-f"]

    # Create the secret dbs and add the secret keys and values to it
    base_add_secret_cmd = base_plugin_cmd + ["add", "-f"]
    for secret_db_key, secret_db in secret_db.items():
        # Create the secret db if it doesn't exist
        if not exists(secret_db["path"]):
            new_db_cmd = create_db_cmd + [secret_db["path"]]
            execute_kwargs = {"commands": [new_db_cmd], "capture": True}
            results = process(execute_kwargs=execute_kwargs)
            for result in results:
                json_result = format_output_json(result)
                if (
                    "status" in json_result["error"]
                    and json_result["error"]["status"] == "failed"
                ):
                    if "msg" in json_result["error"]:
                        response["msg"] = json_result["error"]["msg"]
                        return False, response
                    else:
                        response["msg"] = json_result
                        return False, response
                print(
                    "Created secret db: {} by running: {} with output: {}".format(
                        secret_db_path, new_db_cmd, json_result["output"]
                    )
                )

        # Assign the 'data' key and it's content to the secret_db's secret file
        db_add_cmd = base_add_secret_cmd + [secret_db["path"]]
        for key, value in secret_db["data"].items():
            # The value added to the secret_db
            # must be a value of type str, bytes, or pathlike
            added, response = add_secret(db_add_cmd, key, value)
            if not added:
                return False, response
            print("Assigned key: {} to secret db: {}".format(key, secret_db["path"]))

    response["msg"] = "The secrets db at: {} was used to configure the server".format(
        secret_db_path
    )
    return True, response


if __name__ == "__main__":
    new_dir, msg = init_secrets_dir()
    if not new_dir:
        print(msg)
        exit(1)

    configured_secrets, msg = configure_secrets()
    if not configured_secrets:
        print(msg)
        exit(1)

    del_secrets_dir, msg = del_secrets_dir()
    if not del_secrets_dir:
        print(msg)
        exit(1)
