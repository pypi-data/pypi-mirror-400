import json
import logging
import os
from git_sanity import __prog_name__
from git_sanity import __config_root_dir__
from git_sanity import __gitsanity_config_file_name__
from git_sanity import __local_config_file_name__
from git_sanity.utils import run

gitsanity_default_config = {
    "this_is_a_comment_example": "<!--JSON-style comment markers (similar to HTML comments)-->",
    "code_hosting_platform": "<!--code hosting platform, eg:gitcode-->",
    "projects": [
        {
            "name": "<!--project's name-->",
            "owner": "<!--organization or individual to which the project belongs.-->",
            "path": "project's path on the code hosting platform",
            "branch": "<!--branch's name-->",
            "local_path": "<!--local path to clone repo, default=.>",
            "forward_to_git": {
                "clone": ["<!--command args of git clone, eg:--depth=1000-->"],
                "fetch": ["<!--command args of git fetch, eg:--depth=1000-->"]
            }
        }
    ],
    "groups": [
        {
            "group_name": "all",
            "projects": [
                "<!--project_name, default=[]-->"
            ]
        }
    ],
    "commands" : [
        {"<!--command_name-->": ["<!--command and command args-->"]},
        {"<!--test-->": ["<!-- ls -->", "<!-- -l -->"]}
    ]
}


def create_or_get_gitsanity_config(url, branch, working_directory):
    repo_path = os.path.join(working_directory, __config_root_dir__)
    clone_cmd = ["git", "clone", url, __config_root_dir__]
    if url and branch:
        clone_cmd.extend(["-b", branch])
    elif branch:
        logging.error("When -b/--branch is specified, -u/--url must exist")
        exit(1)
    if url and run(clone_cmd, workspace=working_directory).returncode == 0:
        return
    elif url:
        logging.error(f"Failed to initialize {__prog_name__} with {url}")
        exit(1)
    else:
        os.mkdir(repo_path)
        config_file_path = os.path.join(repo_path, __gitsanity_config_file_name__)
        with open(config_file_path, "w", encoding="utf-8") as f:
            json.dump(gitsanity_default_config, f, indent=4, ensure_ascii=False)
        logging.warning(f"Default config file created at {config_file_path}. Customize as needed.")
        return


local_default_config = {
    "working_branch": ""
}


def try_to_careate_local_config(working_directory):
    local_config_file_path = os.path.join(working_directory, __config_root_dir__, __local_config_file_name__)
    if os.path.exists(local_config_file_path):
        return

    with open(local_config_file_path, "w", encoding="utf-8") as f:
        json.dump(local_default_config, f, indent=4, ensure_ascii=False)


def init_impl(args):
    """
    Initialize a git-sanity repository with optional URL or local configuration
    
    Parameters:
    - args: Command-line arguments object containing:
        * directory: Target directory for repository
        * URL: Optional remote repository URL for cloning
        
    Returns:
    - None (exits with status code 0 on success, 1 on failure)
    """
    if not os.path.isdir(args.directory):
        logging.error(f"The value of -d/--directory is not a valid path: {args.directory}")
        exit(1)

    repo_path = os.path.join(args.directory, __config_root_dir__)
    if os.path.isdir(repo_path):
        logging.error(f"Reinitialized existing {__prog_name__} repository in {args.directory}")
        exit(0)

    create_or_get_gitsanity_config(args.url, args.branch, args.directory)
    try_to_careate_local_config(args.directory)

