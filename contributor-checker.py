#!/usr/bin/env python3
#===================================================
# This tool helps to generate a report on commit contributors for a specific Git branch. 
# It fetches commit details, filters contributors by email domain, and generates a detailed report with pie charts.
#
# Author: Hemanth Selam
# Email: hemanth.selam@gmail.com
# Version: 20241219
#==================================================
import subprocess
import argparse
import pandas as pd
import re
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import datetime

__version__ = "20241219"
__author__ = "Hemanth Selam"
__author_email__ = "Hemanth.Selam@gamil.com"

def run_git_command(command):
    """Run a git command and return the output."""
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(f"Error running command: {' '.join(command)}")
        print(result.stderr)
        exit(1)
    return result.stdout.strip()

def checkout_branch(branch):
    """Checkout to the specified branch."""
    print(f"Checking out to branch: {branch}")
    # Checkout into given branch
    run_git_command(['git', 'checkout', branch])

def get_commit_log(branch, domain):
    """Get the commit log for the specified branch."""
    print(f"Collecting log for branch: {branch}")
    git_cmd = ['git', 'log', branch, '--pretty=oneline']
    ret_output = run_git_command(git_cmd)
    commit_id_list = []
    find_all_commit_id = re.findall(r'[0-f]+\s+.*', ret_output)
    if find_all_commit_id:
        final_id = [each_id.split(" ")[0] for each_id in find_all_commit_id]
        commit_id_list.extend(final_id)
    total_commit_id = len(commit_id_list)
    print("Total commits: ", total_commit_id)
    #Configure the number of commits
    #commit_id_list = commit_id_list[:10]
    data = []
    # Extract data from each commit
    for each_cmt_id in commit_id_list:
        ret_str = run_git_command(['git', 'show', f'{each_cmt_id}'])
        ret_data = parse_commit_log(ret_str, domain)
        data.append(ret_data)
    return data, total_commit_id

def parse_commit_log(commit_log, domain):
    final_dict = {}
    commit_dict = {}
    commit_key = ''
    split_lines = commit_log.split("\n")
    for ind, each_line in enumerate(split_lines):
        regex_for_commit_line = re.search(r'^commit\s+([0-f]+)$', each_line)
        if regex_for_commit_line:
            commit_key = regex_for_commit_line.group(1)

        regex_for_signed_off = re.search(rf'Signed.*by:\s+(.*)(\<.*@{domain}\>)', each_line)
        regex_for_signed_off_pre_line = re.search(r'Signed.*by:\s+(.*\<.*@.*.com\>)', split_lines[ind-1])
        if regex_for_signed_off and regex_for_signed_off_pre_line:
            name = regex_for_signed_off.group(1)
            email_id = regex_for_signed_off.group(2).replace('<', '').replace('>', '')
            if commit_dict:
                temp = {'SHAID': commit_key, 'name': name.strip(), 'email_id': email_id.strip()}
                temp.update(commit_dict)
                final_dict.update({commit_key: temp})
            else:
                final_dict.update({commit_key: {'SHAID': commit_key, 'name': name, 'email_id': email_id}})

        regex_for_commit_msg = re.search(r'Date.*\d+:\d+:\d+.*$', split_lines[ind - 2])
        if regex_for_commit_msg:
            commit_dict.update({'commit_message': each_line.strip()})

    return final_dict

def create_html_report(data, branch, domain, total_commit_id):
    """Create an HTML report from the data."""
    data_list = []
    for each_dict in data:
        for key, value in each_dict.items():
            data_list.append(value)

    final_data_list = [
        {
            "SHAID": each_dict.get("SHAID", ""),
            "Commit Message": each_dict.get("commit_message", ""),
            "Name": each_dict.get("name", ""),
            "Mail ID": each_dict.get("email_id", ""),
        }
        for each_dict in data_list
    ]

    df = pd.DataFrame(final_data_list, columns=["SHAID", "Commit Message", "Name", "Mail ID"])

    if df.empty:
        print("No data available to generate the report.")
        return

    # Adjust index to start from 1
    df.index = range(1, len(df) + 1)

    # Summary table: Contributor Name and Number of Commits
    summary = df["Name"].value_counts().reset_index()
    summary.columns = ["Contributor Name", "Number of Commits"]
    summary.index = range(1, len(summary) + 1)  # Start summary table index from 1

    # Split contributors into domain and non-domain groups
    domain_contributors = df[df["Mail ID"].str.contains(f"@{domain}", na=False)]

    domain_count = len(domain_contributors)
    non_domain_count = max(total_commit_id - domain_count, 0)

    # Log values for debugging
    print(f"{domain} Count: {domain_count}")
    print(f"Non-{domain} Count: {non_domain_count}")

    # Total commit counts table
    summary_table = pd.DataFrame({
        "Contributor Type": [f"{domain} Contributors", "Non-{domain} Contributors", "Total Commits"],
        "Number": [domain_count, non_domain_count, total_commit_id],
    })

    # First Pie Chart: Contribution Summary
    plt.figure(figsize=(8, 8))
    plt.pie(
        summary["Number of Commits"],
        labels=summary["Contributor Name"],
        autopct="%1.1f%%",
        startangle=140,
        textprops={"fontsize": 8},
    )
    plt.axis("equal")
    plt.title("Commit Contribution Summary")
    pie_buffer = BytesIO()
    plt.savefig(pie_buffer, format="png", bbox_inches="tight")
    pie_data = base64.b64encode(pie_buffer.getvalue()).decode()
    pie_buffer.close()

    # Second Pie Chart: Domain vs Non-Domain Contributors
    plt.figure(figsize=(8, 8))

    # Ensure that both counts are valid
    if domain_count >= 0 and non_domain_count >= 0:
        # Set a threshold for when values are too small to be displayed properly
        if domain_count < 1:
            domain_count = 1  # Minimum 1 for visualization
        if non_domain_count < 1:
            non_domain_count = 1  # Minimum 1 for visualization

        plt.pie(
            [domain_count, non_domain_count],
            labels=[f"{domain} Contributors", "Non-{domain} Contributors"],
            autopct="%1.1f%%",
            startangle=140,
            textprops={"fontsize": 8},
            colors=['#4CAF50', '#FF5733']  # Optional custom colors for distinction
        )
        plt.axis("equal")
        plt.title(f"{domain} vs Non-{domain} Contributors")
        pie_buffer2 = BytesIO()
        plt.savefig(pie_buffer2, format="png", bbox_inches="tight")
        pie_data2 = base64.b64encode(pie_buffer2.getvalue()).decode()
        pie_buffer2.close()
    else:
        print(f"Error: Invalid {domain} count or non-{domain} count. {domain}: {domain_count}, Non-{domain}: {non_domain_count}")

    # HTML Styling
    table_style = """
    <style>
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
    }
    th {
        background-color: #f2f2f2;
        text-align: left;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    tr:hover {
        background-color: #f1f1f1;
    }
    </style>
    """

    # Generate the HTML report
    with open("contributor-report.html", "w") as f:
        f.write("<html><head>")
        f.write(table_style)
        f.write(f"""</head> <body> <h1>Commit Contributors Report:</h1> <h2>Branch: {branch}</h2>""")
        f.write(df.to_html(index=True, border=0, escape=False, classes="table"))
        f.write("<h2>Summary</h2>")
        f.write(summary.to_html(index=True, border=0, escape=False, classes="table"))
        f.write(summary_table.to_html(index=False, border=0, escape=False, classes="table"))
        f.write(f'<img src="data:image/png;base64,{pie_data}" alt="Pie Chart">')
        f.write(f'<img src="data:image/png;base64,{pie_data2}" alt="Pie Chart">')
        f.write("</body></html>")
    print("Report generated successfully: contributor-report.html")


def main():
    #parser = argparse.ArgumentParser(description='Check contributors for commits in a particular branch.',formatter_class=argparse.RawTextHelpFormatter)
    parser = argparse.ArgumentParser(prog='contributor-checker', description='Check contributors for commits in a particular branch.', usage='%(prog)s -b=<branch> -d=<domain> [-v] [-h]')
    parser.add_argument('-b', '--branch', required=True, help='Branch name to check')
    parser.add_argument('-d', '--domain', required=True, help='Domain to filter signed-off-by emails')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__} ~ {__author__} ({__author_email__})', help='Show version and author info')
    args = parser.parse_args()

    start_time = datetime.datetime.now()
    print(f"Task started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        checkout_branch(args.branch)
        ret_data, total_commit_id = get_commit_log(args.branch, args.domain)
        create_html_report(ret_data, args.branch, args.domain, total_commit_id)
    except Exception as Err:
        print(f"Observed Exception: {Err}")

    end_time = datetime.datetime.now()
    print(f"Task ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time taken: {end_time - start_time}")

if __name__ == "__main__":
    main()

