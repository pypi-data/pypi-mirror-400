import logging
import os
import random
import string
from git_sanity import __gitsanity_config_file_name__
from git_sanity.utils import run
from git_sanity.utils import get_gitsanity_dir
from git_sanity.utils import load_config
from git_sanity.utils import get_config
from git_sanity.utils import get_project_remote_url
from git_sanity.utils import get_projects_by_group

def sync_impl(args):
    gitsanity_config = load_config(__gitsanity_config_file_name__)
    for project in get_projects_by_group(gitsanity_config, args.group):
        project_name = get_config(project, "name")
        logging.info(f"Syncing source for {project_name}...")
        logging.debug(f"Syncing project={project}")

        repo_path = os.path.join(get_gitsanity_dir(), get_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error(f"The remote {project_name} project branch hasn't been pulled locally yet.")
            continue

        try:
            if args.username:
                upstream_name = ''.join(random.choice(string.ascii_letters) for _ in range(20))
                remote_url = get_project_remote_url("gitcode", None, None,  args.username, project_name)
                run(["git", "remote", "add", upstream_name, remote_url], workspace=repo_path, capture_output=True)
            else:
                upstream_name = "origin"

            branch_to_rebase = args.branch if args.branch else get_config(project, "branch")
            fetch_cmd = ["git", "fetch", upstream_name, branch_to_rebase]
            fetch_cmd.extend(get_config(project, "forward_to_git.fetch", []))
            run(fetch_cmd, workspace=repo_path, capture_output=True)

            rebase_cmd = ["git", "rebase", f"{upstream_name}/{branch_to_rebase}"]
            rebase_cmd.extend(get_config(project, "forward_to_git.rebase", []))
            if run(rebase_cmd, workspace=repo_path).returncode:
                logging.error(f"Failed to rebase {project_name}")
        finally:
            if upstream_name != "origin":
                run(["git", "remote", "remove", upstream_name], workspace=repo_path, capture_output=True)

