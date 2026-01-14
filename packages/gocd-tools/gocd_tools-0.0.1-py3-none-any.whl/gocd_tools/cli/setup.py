from gocd_tools.cli.defaults import SECRETS, SERVER
from gocd_tools.cli.run import cli_exec
from gocd_tools.cli.secrets import add_secrets_groups
from gocd_tools.cli.server import add_server_groups


def setup_cli(parser):
    setup_commands = parser.add_subparsers(title="COMMAND")

    # Secrets
    secrets_parser = setup_commands.add_parser(SECRETS)
    add_secrets_groups(secrets_parser)
    secrets_commands = secrets_parser.add_subparsers(title="COMMAND")
    secrets_init_parser = secrets_commands.add_parser(
        "init",
        help=(
            "Initializes the secrets db directory where the GoCD secrets will be stored."
        ),
    )
    secrets_init_parser.set_defaults(
        func=cli_exec,
        module_path="gocd_tools.secrets",
        module_name="secrets",
        func_name="init_secrets_dir",
    )

    secrets_configure_parser = secrets_commands.add_parser(
        "configure",
        help=(
            "Configure the GoCD server with the secrets defined in the secrets"
            " db directory."
        ),
    )
    secrets_configure_parser.set_defaults(
        func=cli_exec,
        module_path="gocd_tools.secrets",
        module_name="secrets",
        func_name="configure_secrets",
    )

    secrets_del_parser = secrets_commands.add_parser(
        "delete", help="Delete the secrets db directory."
    )
    secrets_del_parser.set_defaults(
        func=cli_exec,
        module_path="gocd_tools.secrets",
        module_name="secrets",
        func_name="del_secrets_dir",
    )

    # Server
    server_parsers = setup_commands.add_parser(SERVER)
    add_server_groups(server_parsers)
    server_commands = server_parsers.add_subparsers(title="COMMAND")
    server_init_parser = server_commands.add_parser(
        "init",
        help=(
            "Initializes the server with an Authorization Configiguration as"
            " defined in the local config directory's authorization_config.yml"
            " file."
        ),
    )
    server_init_parser.set_defaults(
        func=cli_exec,
        module_path="gocd_tools.server",
        module_name="server",
        func_name="init_server",
    )

    server_configure_parser = server_commands.add_parser(
        "configure",
        help=(
            "Configures the designated GoCD server with the configuration"
            " files stored in the local config directory."
        ),
    )
    server_configure_parser.set_defaults(
        func=cli_exec,
        module_path="gocd_tools.server",
        module_name="server",
        func_name="configure_server",
    )

    server_cleanup_parser = server_commands.add_parser(
        "wipe",
        help=(
            "Will wipe all the configuration settings defined in the local"
            " config directory on the GoCD server."
        ),
    )
    server_cleanup_parser.set_defaults(
        func=cli_exec,
        module_path="gocd_tools.server",
        module_name="server",
        func_name="wipe_server",
    )
