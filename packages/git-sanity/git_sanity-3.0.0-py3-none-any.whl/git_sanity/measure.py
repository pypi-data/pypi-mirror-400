import logging
import os
import requests
from git_sanity import __gitsanity_config_file_name__
from git_sanity.utils import run
from git_sanity.utils import get_gitsanity_dir
from git_sanity.utils import load_config
from git_sanity.utils import get_config
from git_sanity.utils import get_projects_by_group
from git_sanity.utils import get_git_username
from git_sanity.utils import get_git_password

def measure_code_changes(username, repo_path, since=None, until=None):
    """
    Measure the code changes made by a specified user in a repository
    
    Args:
        username: Git username
        repo_path: Repository path
        since: Start date for measurement
        until: End date for measurement
    
    Returns:
        dict: Contains added and deleted lines count
    """
    cmd = ["git", "log", "--author", username, "--pretty=tformat:", "--numstat"]
    if since:
        cmd.extend(["--since", since])
    if until:
        cmd.extend(["--until", until])
    
    result = run(cmd, workspace=repo_path, capture_output=True)
    if result.returncode != 0:
        logging.error(f"Failed to get code changes for {repo_path}: {result.stderr}")
        return {"added": 0, "deleted": 0}
    
    added = deleted = 0
    for line in result.stdout.splitlines():
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:
                try:
                    added += int(parts[0]) if parts[0] != '-' else 0
                    deleted += int(parts[1]) if parts[1] != '-' else 0
                except ValueError:
                    continue
    return {"added": added, "deleted": deleted, "total": added - deleted}


def measure_pr_count(username, project, password, since=None, until=None):
    """
    Measure the number of PRs created by a specified user on the platform
    
    Args:
        username: Platform username
        project: Project configuration
        password: Access token
        since: Start date for measurement
        until: End date for measurement
    
    Returns:
        int: Number of PRs
    """
    # Get owner and project name from project configuration
    owner = get_config(project, "owner")
    project_name = get_config(project, "name")
    
    # Build API request URL
    headers = {
        'Authorization': f'Bearer {password}',
        'Accept': 'application/json'
    }
    
    # Get PR list
    url = f"https://api.gitcode.com/api/v5/repos/{owner}/{project_name}/pulls"
    params = {
        'state': 'merged',
        'author': username
    }
    
    if since:
        params['merged_after'] = since
    if until:
        # GitCode API uses created parameter to limit end time
        params['merged_before'] = f"<={until}"
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            prs = response.json()
            return len(prs)
        else:
            logging.error(f"Failed to fetch PRs for {owner}/{project_name}: {response.status_code}")
            return 0
    except requests.exceptions.RequestException as e:
        logging.error(f"Network request error when fetching PRs: {e}")
        return 0


def measure_impl(args):
    """
    Implement user contribution measurement functionality
    
    Args:
        args: Command line arguments including username, password, time range, project group, etc.
    """
    gitsanity_config = load_config(__gitsanity_config_file_name__)
    username = get_git_username() if args.username is None and args.password is None else args.username
    password = get_git_password() if args.username is None and args.password is None else args.password
    if username is None:
        logging.error("Please enter the username of the user to be measured.")
        exit(1)
    if password is None:
        logging.warning("The password is not entered. Only the number of modified codes is measured.")

    # Total statistics results
    total_code_changes = {"added": 0, "deleted": 0, "total": 0}
    total_pr_count = 0

    for project in get_projects_by_group(gitsanity_config, args.group):
        project_name = get_config(project, "name")
        logging.info(f"Measuring contribution for {project_name}...")
        logging.debug(f"Measuring project={project}")

        # Repository path
        repo_path = os.path.join(get_gitsanity_dir(), get_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error(f"The remote {project_name} project branch hasn't been pulled locally yet.")
            continue

        # Call function to measure merged code changes
        code_changes = measure_code_changes(username, repo_path, args.since, args.until)
        total_code_changes["added"] += code_changes["added"]
        total_code_changes["deleted"] += code_changes["deleted"]
        total_code_changes["total"] += code_changes["total"]

        # If password is provided, get PR count
        if password is not None:
            # Call function to measure PR count
            pr_count = measure_pr_count(username, project, password, args.since, args.until)
            total_pr_count += pr_count

        # Output current project's statistics
        print(f"{project_name} Contribution Summary:")
        print(f"  Code Changes: +{code_changes['added']} -{code_changes['deleted']} {code_changes['total']}")
        if password is not None:
            print(f"  PR Count: {pr_count}")

    # Output all projects' statistics
    print(f"Total Contribution Summary:")
    print(f"  Total Code Changes: +{total_code_changes['added']} -{total_code_changes['deleted']} {total_code_changes['total']}")
    if password is not None:
        print(f"  Total PR Count: {total_pr_count}")