import logging
import os
from git_sanity import __gitsanity_config_file_name__
from git_sanity.utils import run
from git_sanity.utils import get_gitsanity_dir
from git_sanity.utils import load_config
from git_sanity.utils import get_config
from git_sanity.utils import get_project_remote_url
from git_sanity.utils import get_projects_by_group

def clone_impl(args):
    """
    Implements the clone operation for multiple projects based on user configuration
    
    This function:
    1. Loads user configuration from arguments
    2. Retrieves all projects belonging to the specified group
    3. Clones each project using git clone with configured parameters
    4. Handles optional forward_to_git parameters
    5. Uses configured workspace or current directory as default
    
    Args:
        args: Command-line arguments containing group name and other configuration
        
    Returns:
        None (performs side effects by cloning repositories)
    """
    gitsanity_config = load_config(__gitsanity_config_file_name__)
    for project in get_projects_by_group(gitsanity_config, args.group):
        project_name = get_config(project, "name")
        project_branch = get_config(project, "branch")
        logging.info(f"Cloning {project_name}...")
        logging.debug(f"Cloning project={project}")

        remote_url = get_project_remote_url("gitcode", None, None, get_config(project, "owner"), project_name)
        clone_cmd = ["git", "clone", remote_url, "-b", project_branch]
        clone_cmd.extend(get_config(project, "forward_to_git.clone", []))

        workspace = os.path.join(get_gitsanity_dir(), get_config(project, "local_path", "."))
        if run(clone_cmd, workspace=workspace).returncode:
            logging.error(f"Failed to clone {project_name}")
            continue

        repo_path = os.path.join(workspace, project_name)
        if run(["git", "checkout", f"origin/{project_branch}"], workspace=repo_path, capture_output=True).returncode:
            continue
        run(["git", "branch", "-d", project_branch], workspace=repo_path, capture_output=True)
    logging.warning(f"Use `git-sanity switch` to switch working branche.")
