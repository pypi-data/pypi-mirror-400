import logging
import os
from git_sanity import __gitsanity_config_file_name__
from git_sanity.utils import run
from git_sanity.utils import get_gitsanity_dir
from git_sanity.utils import load_config
from git_sanity.utils import get_config
from git_sanity.utils import get_projects_by_group
from git_sanity.utils import get_git_username
from git_sanity.utils import get_git_password
from git_sanity.utils import get_project_remote_url
from git_sanity.utils import parse_username_aliasname

def fetch_impl(args):
    user_config = load_config(__gitsanity_config_file_name__)
    for project in get_projects_by_group(user_config, args.group):
        project_name = get_config(project, "name")
        logging.info(f"Fetching source for {project_name}...")
        logging.debug(f"Fetching project={project}")

        repo_path = os.path.join(get_gitsanity_dir(), get_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error(f"The remote {project_name} project branch hasn't been pulled locally yet.")
            continue

        # if args.username:
        #     username, aliasname = parse_username_aliasname(args.username)
        #     remotes = run(["git", "remote", "-v"], workspace=repo_path, capture_output=True).stdout.strip().split('\n')
        #     remote_names = [remote.split('\t', 1)[0] for remote in remotes]
        #     if aliasname not in remote_names:
        #         remote_url = get_project_remote_url("gitcode", None, None, username, get_config(project, "path"))
        #         run(["git", "remote", "add", aliasname, remote_url], workspace=repo_path, capture_output=True)
        #     remote_name = aliasname
        # else:
        #     remote_name = "origin"
        if args.username:
            remotes = run(["git", "remote", "-v"], workspace=repo_path, capture_output=True).stdout.strip().split('\n')
            remote_names = [remote.split('\t', 1)[0] for remote in remotes]
            if args.username not in remote_names:
                remote_url = get_project_remote_url("gitcode", None, None, args.username, get_config(project, "path"))
                run(["git", "remote", "add", args.username, remote_url], workspace=repo_path, capture_output=True)
            remote_name = args.username
        else:
            remote_name = "origin"

        fetch_cmd = ["git", "fetch", remote_name]
        fetch_cmd.extend(get_config(project, "forward_to_git.fetch", []))
        if args.branch:
            fetch_cmd.append(args.branch)
        if run(fetch_cmd, workspace=repo_path).returncode:
            logging.error(f"Failed to fetch {project_name}")
