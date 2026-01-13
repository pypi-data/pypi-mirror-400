import logging
import os
from git_sanity import __config_root_dir__
from git_sanity import __gitsanity_config_file_name__
from git_sanity.utils import run
from git_sanity.utils import get_gitsanity_dir
from git_sanity.utils import load_config
from git_sanity.utils import get_config
from git_sanity.utils import get_projects_by_group

def branch_impl(args):
    """
    Implementation for managing Git branches across multiple projects.
    
    Args:
        args: Command-line arguments containing:
            - group (str): Group name to filter projects
            - delete (str): Branch name to delete (non-force)
            - force_delete (str): Branch name to force delete
    
    Returns:
        None
    """
    if args.delete is None and args.force_delete is None:
        logging.info(f"Processing branches for .git-sanity...")
        run(["git", "branch"], workspace=os.path.join(get_gitsanity_dir(), __config_root_dir__))

    gitsanity_config = load_config(__gitsanity_config_file_name__)
    for project in get_projects_by_group(gitsanity_config, args.group):
        project_name = get_config(project, "name")
        logging.info(f"Processing branches for {project_name}...")
        logging.debug(f"Processing project={project}")

        repo_path = os.path.join(get_gitsanity_dir(), get_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error(f"The remote {project_name} project branch hasn't been pulled locally yet.")
            exit(1)

        branch_cmd = ["git", "branch"]
        branch_cmd.extend(get_config(project, "forward_to_git.branch", []))
        if args.delete is not None:
            branch_cmd.extend(["-d", args.delete])
        elif args.force_delete is not None:
            branch_cmd.extend(["-D", args.force_delete])
        run(branch_cmd, workspace=repo_path)
