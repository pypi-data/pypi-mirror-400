import logging
import os
from git_sanity import __config_root_dir__
from git_sanity import __gitsanity_config_file_name__
from git_sanity import __local_config_file_name__
from git_sanity.utils import run
from git_sanity.utils import get_gitsanity_dir
from git_sanity.utils import load_config
from git_sanity.utils import get_config
from git_sanity.utils import get_projects_by_group
from git_sanity.utils import update_config

def get_all_branches(remote_name, local_repo_path: str):
    local_branch_result = run(["git", "branch"], workspace=local_repo_path, capture_output=True)
    if local_branch_result.returncode:
        logging.error(f"Failed to get local branch: {local_branch_result.stderr}")
        return None, None
    local_branches = [
        branch.strip('* ').strip() for branch in local_branch_result.stdout.split('\n') if branch.strip()
    ]

    remote_branch_result = run(["git", "branch", "-r"], workspace=local_repo_path, capture_output=True)
    if remote_branch_result.returncode:
        logging.error(f"Failed to get remote branch: {remote_branch_result.stderr}")
        return local_branches, None
    remote_branches = [
        branch.strip().replace(f'{remote_name}/', '') for branch in remote_branch_result.stdout.split('\n') if branch.strip() and '->' not in branch
    ]
    return local_branches, remote_branches


def switch_impl(args):
    """
    Implements the branch switching functionality for multiple projects based on group configuration.

    Parameters:
    - args: Command-line arguments containing:
        - group: Name of the group to switch branches for
        - new_branch_name: Optional name for the new branch to create (if provided)
        - branch_name: Optional name of the existing branch to switch to (if provided)

    Returns:
    - None (exits with error code 1 on failure)
    """
    gitsanity_config = load_config(__gitsanity_config_file_name__)
    projects_of_group = get_projects_by_group(gitsanity_config, args.group)
    if not projects_of_group:
        return

    for project in projects_of_group:
        project_name = get_config(project, "name")
        logging.info(f"Switching branch for {project_name}...")
        logging.debug(f"Switching project={project}")

        repo_path = os.path.join(get_gitsanity_dir(), get_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error(f"The remote {project_name} project branch hasn't been pulled locally yet.")
            continue

        if args.username:
            remotes = run(["git", "remote", "-v"], workspace=repo_path, capture_output=True).stdout.strip().split('\n')
            remote_names = [remote.split('\t', 1)[0] for remote in remotes]
            if args.username not in remote_names:
                logging.error(f"The remote {args.username} doesn't exist. please `git-sanity fetch -u {args.username}` first.")
                continue
            remote_name = args.username
        else:
            remote_name = "origin"

        local_branch_result, remote_branch_result = get_all_branches(remote_name, repo_path)
        logging.debug(f"Local branches of {project_name}: {local_branch_result}")
        logging.debug(f"Remote branches of {project_name}: {remote_branch_result}")
        if args.branch_name in local_branch_result:
            switch_cmd = ["git", "checkout", f"{args.branch_name}"]
        elif args.branch_name in remote_branch_result:
            switch_cmd = ["git", "checkout", "-b", args.branch_name, f"{remote_name}/{args.branch_name}"]
        else:
            switch_cmd = ["git", "checkout", "-b", args.branch_name, f"{remote_name}/{get_config(project, 'branch')}"]
        switch_cmd.extend(get_config(project, "forward_to_git.switch", []))
        result = run(switch_cmd, workspace=repo_path, capture_output=True)
        if result.returncode:
            logging.error(f"Failed to switch {project_name}'s branch to {args.branch_name}: {result.stderr}")
    update_config(__local_config_file_name__, "working_branch", args.branch_name)


def upstream_impl(args):
    gitsanity_dir = os.path.join(get_gitsanity_dir(), __config_root_dir__)
    local_branch_result, remote_branch_result = get_all_branches("origin", gitsanity_dir)
    logging.debug(f"Local branches of .git-sanity: {local_branch_result}")
    logging.debug(f"Remote branches of .git-sanity: {remote_branch_result}")
    if args.branch in local_branch_result:
        switch_cmd = ["git", "checkout", f"{args.branch}"]
    elif args.branch in remote_branch_result:
        switch_cmd = ["git", "checkout", "-b", args.branch, f"origin/{args.branch}"]
    else:
        logging.error(f"`{args.branch}` is not an existing branch")
        return
    result = run(switch_cmd, workspace=gitsanity_dir, capture_output=True)
    if result.returncode:
        logging.error(f"Failed to switch .git-sanity's branch to {args.branch}: {result.stderr}")
