import logging
import os
from git_sanity import __prog_name__
from git_sanity import __gitsanity_config_file_name__
from git_sanity import __local_config_file_name__
from git_sanity.utils import run
from git_sanity.utils import get_gitsanity_dir
from git_sanity.utils import load_config
from git_sanity.utils import get_config
from git_sanity.utils import get_projects_by_group
from git_sanity.utils import get_git_username
from git_sanity.utils import get_git_password
from git_sanity.utils import get_project_remote_url
from git_sanity.cherry_pick import get_prs_by_issue_id


def current_branch_has_remote_pr(current_branch: str,
    target_repo_owner: str, target_repo_path: str,
    repo_path_of_issue: str, issue_id: int):
    for pr in get_prs_by_issue_id(target_repo_owner, repo_path_of_issue, issue_id):
        target_repo_path_of_pr = pr["base"]["repo"]["path"]
        source_repo_branch_of_pr = pr["head"]["ref"]
        if target_repo_path_of_pr == target_repo_path and source_repo_branch_of_pr == current_branch:
            return True
        else:
            return False


def create_pr_for_remote_repo(target_repo_owner: str, target_repo_path: str, repo_path_of_issue: str, issue_id: int):
    pass


def push_impl(args):
    local_config = load_config(__local_config_file_name__)
    working_branch = get_config(local_config, "working_branch")
    if not working_branch:
        logging.error(f"working_branch is not set. Please set it via `{__prog_name__} switch` command")
        exit(1)

    gitsanity_config = load_config(__gitsanity_config_file_name__)
    for project in get_projects_by_group(gitsanity_config, args.group):
        project_name = get_config(project, "name")
        logging.info(f"Pushing {project_name}...")
        logging.debug(f"Pushing project={project}")

        repo_path = os.path.join(get_gitsanity_dir(), get_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error(f"The remote {project_name} project branch hasn't been pulled locally yet")
            exit(1)

        current_branch = run(["git", "branch", "--show-current"], workspace=repo_path, capture_output=True).stdout.strip()
        if not current_branch:
            logging.error(f"Failed to get current branch for repo at {repo_path}")
            exit(1)
        elif current_branch != working_branch:
            logging.warning(f"The current branch of {project_name} is not the working branch ({working_branch}), skipped push")
            continue

        check_result = run(["git", "log", f"origin/{get_config(project, 'branch')}..HEAD"], workspace=repo_path, capture_output=True)
        if check_result.returncode or check_result.stderr.strip():
            logging.error(f"Failed to check for commits to push for repo at {repo_path}: {check_result.stderr}")
            exit(1)
        elif not check_result.stdout.strip():
            logging.warning(f"{project_name} no change, skip push")
            continue

        username = args.username if args.username else get_git_username()
        password = args.password if args.password else get_git_password()
        remote = get_project_remote_url("gitcode", username, password, username, get_config(project, "path"))
        check_result = run(["git", "ls-remote", "--heads", remote], workspace=repo_path, capture_output=True)
        if check_result.returncode or check_result.stderr.strip():
            logging.error(f"{remote} cannot be accessed: {check_result.stderr}")
            exit(1)

        original_git_credential_helper = run(["git", "config", "--global", "credential.helper"], workspace=repo_path, capture_output=True).stdout.strip()
        try:
            run(["git", "config", "--global", "--unset-all", "credential.helper"], workspace=repo_path, capture_output=True)

            push_cmd = ["git", "push", remote, current_branch]
            if args.force:
                push_cmd.append("--force")
            result = run(push_cmd, workspace=repo_path, capture_output=True)
            if result.returncode:
                logging.error(f"Failed to push commits of {project_name} to remote: {result.stderr}")
                exit(1)
            else:
                logging.info(f"Successfully pushed")
        finally:
            run(["git", "config", "--global", "credential.helper", original_git_credential_helper], workspace=repo_path, capture_output=True)
