def import_from_module(module_path, module_name, func_name):
    module = __import__(module_path, fromlist=[module_name])
    return getattr(module, func_name)


def cli_exec(args):
    # Action determines which function to execute
    module_path = args.module_path
    module_name = args.module_name
    func_name = args.func_name
    func = import_from_module(module_path, module_name, func_name)
    if not func:
        return False

    # Extract none config kwargs from args
    return func()
