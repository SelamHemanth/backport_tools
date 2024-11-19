import os 
import subprocess 
import sys 
from termcolor import colored

VERSION = "1.0.1" 
AUTHOR = "Hemanth Selam" 
EMAIL = "hemanth.selam@gmail.com" 
LICENSE = "MIT"

def print_help(): 
    help_message = f""" 
Review Request Generator Tool

Description: 
This tool generates an HTML review request for backported Linux kernel patches. 
The generated HTML file lists the patches with links to the corresponding 
backported and upstream commits. Also, It checks the diffrence between upstream
and backport patch.

Usage:
    review-request <distro_name> <branch_name> <num_commits> <repo_name> [dir_path] [--check-diffs]

Arguments:
    <distro_name>  : The name of the Linux distribution.
    <branch_name>  : The name of the branch where the backported patches are applied.
    <num_commits>  : The number of recent commits to include in the review request.
    <repo_name>    : The repository to use (linux, qemu, libvirt, ovmf).
    [dir_path]     : (Optional) Path to a directory containing the commits.
    [--check-diffs]: (Optional) Check diffs between upstream and backport patches.
    
    [--help]       : Help
    [--version]    : Displays version.

Output:
    Generates a 'review_request.html' file in the current directory.

Author:
    Name: {AUTHOR}
    Email: {EMAIL} 
""" 
    print(help_message) 

def show_version(): 
    print(f"Review Request Generator version {VERSION}") 
    print(f"Author: {AUTHOR}") 
    print(f"Email: {EMAIL}") 
    print(f"License: {LICENSE}") 

def get_commit_info(num_commits, commit_dir=None): 
    log_format = "%H%n%B%n---END---" 

    backport_ids = []
    upstream_ids = []
    commit_msgs = []
    signed_off_lines = []

    command = f"git -C {commit_dir} log -n {num_commits} --pretty=format:'{log_format}'" if commit_dir else \
        f"git log -n {num_commits} --pretty=format:'{log_format}'"

    subprocess.run(command, shell=True, capture_output=True)

    commit_header = ""
    commit_body = ""

    for entry in subprocess.run(command, shell=True, capture_output=True).stdout.decode().splitlines():
        entry = entry.strip()
        if entry == "---END---":
            backport_id = commit_header.replace('commit ', '')
            commit_msg = commit_body.split('\n')[0] 
            upstream_id = "N/A" 
            for line in commit_body.split('\n'): 
                if 'commit ' in line and 'upstream' in line: 
                    upstream_id = line.split(' ')[1] 
                    break 
            signed_off = "" 
            for line in commit_body.split('\n'): 
                if 'Signed-off-by: ' in line: 
                    signed_off = line.split('Signed-off-by: ')[1]
                    signed_off_lines.append(signed_off)

            backport_ids.append(backport_id)
            upstream_ids.append(upstream_id)
            commit_msgs.append(commit_msg)

            commit_header = ""
            commit_body = ""
        elif not commit_header:
            commit_header = entry
        else:
            commit_body += entry + '\n'

    return backport_ids, upstream_ids, commit_msgs, signed_off_lines

def check_diff(backport_id, upstream_id, repo_dir):
    """
    Perform a diff check between backport and upstream commits.
    """ 
    backport_file = "/tmp/backport" 
    upstream_file = "/tmp/upstream" 

    # Extract 'git show' content for each commit 
    subprocess.run(f"git -C {repo_dir} show {backport_id} > {backport_file}", shell=True) 
    subprocess.run(f"git -C {repo_dir} show {upstream_id} > {upstream_file}", shell=True) 

    # Perform the diff check 
    diff_command = f"diff {upstream_file} {backport_file}" 
    diff_process = subprocess.run(diff_command, shell=True, capture_output=True, text=True) 
    diff_output = diff_process.stdout.splitlines()

    meaningful_diff = any(
        line.startswith(("< +", "> +" ,"> -", "< -"))
        for line in diff_output
    )

    return diff_output, meaningful_diff

def display_diff_status(backport_ids, upstream_ids, repo_dir):
    """
    Display the diff status in the console.
    """
    print("Performing diff checks...")
    for i, (backport_id, upstream_id) in enumerate(zip(backport_ids, upstream_ids)):
        if upstream_id == "N/A":
            print(colored(f"[Patch-{i + 1}]: No Upstream Commit Found", "yellow"))
            continue

        # Check the diff status
        raw_diff_output, has_diff = check_diff(backport_id, upstream_id, repo_dir)
        
        if has_diff:
            print(
                colored(f"[Patch-{i + 1}]: Difference Found", "red"),
                colored(f"Backport: {backport_id[:14]}", "cyan"),
                colored(f"Upstream: {upstream_id[:14]}", "cyan"),
                sep="\n",
            )
            print("\n".join(raw_diff_output))
        else:
            print(colored(f"[Patch-{i + 1}]: No Difference", "green"))

def generate_review_request(distro_name, branch_name, num_commits, repo_name, commit_dir=None, check_diffs=False):
    base_url_backport = "https://github.com/AMDEPYC/Linux_Backport/commit/"
    base_url_upstream = {
        "linux": "https://github.com/torvalds/linux/commit/",
        "qemu": "https://github.com/qemu/qemu/commit/",
        "libvirt": "https://github.com/libvirt/libvirt/commit/",
        "ovmf": "https://github.com/tianocore/edk2/commit/"
    }.get(repo_name, None) 

    if not base_url_upstream: 
        print(f"Unsupported repository: {repo_name}") 
        sys.exit(1) 

    backport_ids, upstream_ids, commit_msgs, signed_off_lines = get_commit_info(num_commits, commit_dir) 

    if len(backport_ids) != num_commits or len(upstream_ids) != num_commits or len(commit_msgs) != num_commits: 
        print("Error: Mismatch in the number of backport IDs, upstream IDs, and commit messages.") 
        print(f"Backport IDs: {len(backport_ids)}")
        print(f"Upstream IDs: {len(upstream_ids)}")
        print(f"Commit Messages: {len(commit_msgs)}")
        sys.exit(1)

    if check_diffs:
        display_diff_status(backport_ids, upstream_ids, commit_dir)

        proceed = input("Do you want to generate the review-request HTML file? (yes/no): ")
        if proceed.lower() != 'yes':
            print("Aborting HTML file generation.")
            sys.exit(0)

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Review Request</title>
</head>
<body>
    <h1>== Review Request ==</h1>
    <p>Please review the backported changes for the following patches for {distro_name} Distro</p>
    <p>Source: <a href="https://github.com/AMDEPYC/Linux_Backport.git">https://github.com/AMDEPYC/Linux_Backport.git</a></p>
    <p>Branch: {branch_name}</p>
"""

    html_content += "<ul>\n"
    # Reverse the commits order to display last commit first
    for i in range(num_commits - 1, -1, -1):
        backport_id_display = backport_ids[i][:14]
        upstream_id_display = upstream_ids[i][:14]

        html_content += f"""
        <li>
            <p> </p>
            <p><strong>{commit_msgs[i]}</strong></p>
            <p>Backported commit id: <a href="{base_url_backport}{backport_ids[i]}">{backport_id_display}</a></p>
            <p>Upstream commit id: <a href="{base_url_upstream}{upstream_ids[i]}">{upstream_id_display}</a></p>
        </li>
""" 

    last_signed_off = signed_off_lines[-1] if signed_off_lines else "Unknown" 

    html_content += f""" 
    </UL> 
    <p>Thanks,</p>
    <p> {last_signed_off} </p>
</body> 
</html> 
""" 

    with open("review_request.html", "w") as file: 
        file.write(html_content)

    print("HTML file 'review_request.html' has been generated.")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--help":
        print_help()
        sys.exit(0)
    elif len(sys.argv) == 2 and sys.argv[1] == "--version":
        show_version()
        sys.exit(0)
    elif len(sys.argv) < 5 or len(sys.argv) > 7:
        print("Usage: review-request <distro_name> <branch_name> <num_commits> <repo_name> [dir_path] [--check-diffs]")
        print("For help: review_request --help")
        sys.exit(1)

    # Parse arguments
    distro_name = sys.argv[1] 
    branch_name = sys.argv[2] 
    num_commits = int(sys.argv[3]) 
    repo_name = sys.argv[4] 
    commit_dir = sys.argv[5] if len(sys.argv) > 5 else None 
    check_diffs = '--check-diffs' in sys.argv 

    generate_review_request(distro_name, branch_name, num_commits, repo_name, commit_dir, check_diffs)

