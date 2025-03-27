#!/usr/bin/env python3
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
Diff Checker Tool

Description:
This tool checks the diffs between backported and upstream commits for patches.

Usage:
    check-diff -p<num_commits> | <sha_id>

Arguments:
    -p<num_commits> : The number of recent commits to include in the diff check.
    <sha_id>        : The commit SHA ID up to which the diff check will be performed.

Options:
    --help, -h      : Display this help message.
    --version, -v   : Display the tool's version information.

Author:
    Name: {AUTHOR}
    Email: {EMAIL}
"""
    print(help_message)

def show_version():
    print(f"Diff Checker Tool version {VERSION}")
    print(f"Author: {AUTHOR}")
    print(f"Email: {EMAIL}")
    print(f"License: {LICENSE}")

def get_commit_info(num_commits=None, sha_id=None):
    log_format = "%H%n%B%n---END---"

    backport_ids = []
    upstream_ids = []
    commit_msgs = []

    if num_commits:
        command = f"git log -n {num_commits} --pretty=format:'{log_format}'"
    elif sha_id:
        command = f"git log --pretty=format:'{log_format}' {sha_id}^..HEAD"
    else:
        print("Either num_commits or sha_id must be provided.")
        sys.exit(1)

    commit_data = subprocess.run(command, shell=True, capture_output=True).stdout.decode()

    commit_header = ""
    commit_body = ""

    for entry in commit_data.splitlines():
        entry = entry.strip()
        if entry == "---END---":
            backport_id = commit_header.replace('commit ', '')
            commit_msg = commit_body.split('\n')[0]
            upstream_id = "N/A"
            for line in commit_body.split('\n'):
                if 'commit ' in line and 'upstream' in line:
                    upstream_id = line.split(' ')[1]
                    break

            backport_ids.append(backport_id)
            upstream_ids.append(upstream_id)
            commit_msgs.append(commit_msg)

            commit_header = ""
            commit_body = ""
        elif not commit_header:
            commit_header = entry
        else:
            commit_body += entry + '\n'

    return backport_ids, upstream_ids, commit_msgs

def check_diff(backport_id, upstream_id):
    """
    Perform a diff check between backport and upstream commits.
    """
    backport_file = "/tmp/backport"
    upstream_file = "/tmp/upstream"

    # Extract 'git show' content for each commit
    subprocess.run(f"git show {backport_id} > {backport_file}", shell=True)
    subprocess.run(f"git show {upstream_id} > {upstream_file}", shell=True)

    # Perform the diff check
    diff_command = f"diff {upstream_file} {backport_file}"
    diff_process = subprocess.run(diff_command, shell=True, capture_output=True, text=True)
    diff_output = diff_process.stdout.splitlines()

    meaningful_diff = any(
        line.startswith(("< +", "> +" ,"> -", "< -"))
        for line in diff_output
    )

    return diff_output, meaningful_diff

def display_diff_status(backport_ids, upstream_ids):
    """
    Display the diff status in the console.
    """
    print("Performing diff checks...")
    for i, (backport_id, upstream_id) in enumerate(zip(backport_ids, upstream_ids)):
        if upstream_id == "N/A":
            print(colored(f"[Patch-{i + 1}]: No Upstream Commit Found", "yellow"))
            continue

        # Check the diff status
        raw_diff_output, has_diff = check_diff(backport_id, upstream_id)

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

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: check-diff -p<num_commits> | <sha_id>")
        sys.exit(1)

    # Parse arguments
    arg = sys.argv[1]

    if arg in ("--help", "-h"):
        print_help()
        sys.exit(0)
    elif arg in ("--version", "-v"):
        show_version()
        sys.exit(0)
    elif arg.startswith("-p"):
        num_commits = int(arg[2:])
        sha_id = None
    else:
        num_commits = None
        sha_id = arg

    backport_ids, upstream_ids, _ = get_commit_info(num_commits=num_commits, sha_id=sha_id)
    display_diff_status(backport_ids, upstream_ids)

