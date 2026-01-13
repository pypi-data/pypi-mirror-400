import json
import logging
import os
import subprocess
from git_sanity import __prog_name__
from git_sanity import __config_root_dir__
from git_sanity import __gitsanity_config_file_name__
from git_sanity import __local_config_file_name__

def run(command, input=None ,workspace="./", env=os.environ, capture_output=False):
    """
    Execute an external command and return its execution result
    
    This function uses subprocess.run() to execute the specified command, 
    supporting execution in a specified working directory and environment,
    with the ability to capture command output and error messages.
    
    Args:
        command (str/list): Command string or command list to execute (e.g., ["ls", "-l"])
        workspace (str): Working directory path for command execution, defaults to current directory(".")
        env (dict): Environment variables dictionary, defaults to os.environ (current process environment)
        capture_output (bool): Whether to capture command's standard output and error output, defaults to False
    
    Returns:
        - When capture_output is True, returns tuple: (stdout_str, stderr_str)
        - When capture_output is False, returns boolean: whether command executed successfully (returncode == 0)
    
    Examples:
        >>> run(["ls", "-l"], capture_output=True)
        ('total 8\n-rw-r--r-- 1 user group 1234 Jan 1 12:34 file.txt', '')
    """
    logging.debug(f"(cwd:{workspace}) Running: {command}")
    result = subprocess.run(
        command,
        input=input,
        cwd=workspace,
        env=env,
        text=True,
        capture_output=capture_output
    )
    logging.debug(f"result: {result}")
    return result


def get_gitsanity_dir(start_path=None):
    if start_path is None:
        start_path = os.getcwd()

    current_path = os.path.abspath(os.path.expanduser(start_path))
    while True:
        config_path = os.path.join(current_path, __config_root_dir__)
        if os.path.isdir(config_path):
            return current_path

        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
            break
        current_path = parent_path
    logging.error("Could not find the git-sanity configuration directory.")
    exit(1)


def load_config(config_file_name):
    gitsanity_dir = get_gitsanity_dir()
    if gitsanity_dir is None:
        logging.error(f"Cannot find {__prog_name__} repository from current path: {os.getcwd()}")
        exit(1)

    config_file_path = os.path.join(gitsanity_dir, __config_root_dir__, config_file_name)
    if os.path.exists(config_file_path):
        with open(config_file_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    else:
        logging.error(f"{config_file_path} does not exist.")
        exit(1)


# JSON-style comment markers (similar to HTML comments)
json_comment_prefix = "<!--"
json_comment_suffix = "-->"
def get_config(config, field_path, default=None):
    """
    Retrieve a nested configuration value with extended path syntax.

    Supported path formats (dot-separated segments):
        - Dictionary access: "projects" or "projects.0.name"
        - Numeric list index: "projects.0.name" accesses the first element of `projects`
        - List filtering: "projects:name=llvm_project.local_path"
                - At segment `projects`, finds the first item where `name == 'llvm_project'`
                    and then continues resolving `.local_path` on that item.

    Behavior:
        - If any segment cannot be resolved the function returns `default`.
        - If `default` is `None` a descriptive error is logged before returning.
        - Values wrapped as JSON-style comments `<!-- ... -->` are treated as
            absent and `default` is returned instead.

    Examples:
        - `get_config(cfg, "projects:name=llvm_project.local_path")`
            returns the `local_path` of the project whose `name` is "llvm_project".
        - `get_config(cfg, "projects.0.name")` returns the `name` of the
            first project in the `projects` list.

    Args:
            config (dict): Configuration dictionary to search through
            field_path (str): Path describing the value to retrieve
            default: Value to return when resolution fails

    Returns:
            The resolved value or `default` if resolution fails or value is commented-out.
    """
    if not field_path:
        return default

    segments = field_path.split('.')
    current = config

    for seg in segments:
        # support filter syntax key:field=value
        if ':' in seg:
            key, filt = seg.split(':', 1)
        else:
            key, filt = seg, None

        # access by key on dict
        if isinstance(current, dict):
            if key in current:
                current = current[key]
            else:
                return default
        # if current is list and key is an integer index
        elif isinstance(current, list) and key.isdigit():
            idx = int(key)
            if 0 <= idx < len(current):
                current = current[idx]
            else:
                return default
        else:
            return default

        # apply list filter if present
        if filt is not None:
            if not isinstance(current, list):
                return default
            if '=' not in filt:
                return default

            fld, val = filt.split('=', 1)
            found = None
            for item in current:
                if isinstance(item, dict) and fld in item and str(item.get(fld)) == val:
                    found = item
                    break
            if found is None:
                return default
            current = found

    # handle JSON-style commented values
    if isinstance(current, str) and current.startswith(json_comment_prefix) and current.endswith(json_comment_suffix):
        return default

    return current


def get_projects_by_group(config, group_name):
    """
    Retrieve all projects belonging to a specified group from user configuration
    
    Args:
        config (dict): Dictionary containing user configuration with 'projects' and 'groups'
        group_name (str): Name of the group to filter projects by
    
    Returns:
        list: List of project dictionaries that belong to the specified group.
              Returns all projects if group_name is "all"
    """
    result_projects = []
    all_projects = get_config(config, "projects", default=[])
    for group in get_config(config, "groups", default=[]):
        if get_config(group, "group_name") != group_name:
            continue

        target_projects = get_config(group, "projects", default=[])
        for project in all_projects:
            if get_config(project, "name", default="") in target_projects:
                result_projects.append(project)
        break
    else:
        if group_name == "all":
            return all_projects

    return result_projects


def update_config(config_file_name, key_path, new_value):
    if isinstance(key_path, str):
        keys = key_path.split('.')
    else:
        keys = key_path

    config = load_config(config_file_name)
    current = config
    for key in keys[:-1]:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            logging.error(f"key_path({key_path}) does not exist")
            return False

    final_key = keys[-1]
    if isinstance(current, dict) and final_key in current:
        current[final_key] = new_value
    else:
        logging.error(f"key_path({key_path}) does not exist")
        return False

    config_file_path = os.path.join(get_gitsanity_dir(), __config_root_dir__, config_file_name)
    with open(config_file_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    return True


def get_git_username():
    try:
        result = run(['git', 'config', 'user.name'], capture_output=True)
        if result.returncode:
            logging.error(f"Failed to automatically retrieve Git's username. Please configure it using `git config --global user.name 'Your Name'`.")
            exit(1)
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"Failed to automatically retrieve Git's username. Please configure it using `git config --global user.name 'Your Name'`.")
        exit(1)


def get_git_password():
    try:
        credential_input = f"protocol=https\nhost=gitcode.com\n\n"
        result = run(['git', 'credential', 'fill'], input=credential_input, capture_output=True)
        if result.returncode:
            logging.error(f"Git credential retrieval failed: {result.stderr}. Use credential.helper to save credentials")
            exit(1)
        for line in result.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1]
    except Exception as e:
        logging.error(f"Git credential retrieval failed: {e}. Use credential.helper to save credentials")
        exit(1)


def get_project_remote_url(code_hosting_platform, unsername, password, project_owner, project_name):
    if unsername is None or password is None:
        return f"https://gitcode.com/{project_owner}/{project_name}.git"
    else:
        return f"https://{unsername}:{password}@gitcode.com/{project_owner}/{project_name}.git"


def parse_username_aliasname(unsername):
    if ':' in unsername:
        parts = unsername.split(':')
        if len(parts) != 2:
            logging.error(f"Invalid username:{unsername} format: multiple or no ':' found")
            exit(1)
        return parts[0].strip(), parts[1].strip()
    else:
        return unsername.strip(), unsername.strip()