import os
import sys


def reload(project_path: str):
    project_path = os.path.normcase(os.path.normpath(project_path))

    for key, value in list(sys.modules.items()):
        if key == "__parents_main__":
            continue

        try:
            package_path = value.__file__
        except AttributeError:
            continue

        if not package_path:
            continue

        package_path = os.path.normcase(os.path.normpath(package_path))

        is_env_package = package_path.startswith(project_path)
        if is_env_package:
            sys.modules.pop(key)
