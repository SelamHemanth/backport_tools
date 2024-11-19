# 🚀 Review Request Generator Tool

## 📄 Description
This tool generates an HTML review request for backported Linux kernel patches. The generated HTML file lists the patches with links to the corresponding backported and upstream commits. It also checks the differences between upstream and backport patches.

## 🛠️ Usage
```bash
	review-request <distro_name> <branch_name> <num_commits> <repo_name> [dir_path] [--check-diffs]
```

## 📋 Arguments
  * 🐧 `distro_name`	: The name of the Linux distribution.
  * 🌿 `branch_name`	: The name of the branch where the backported patches are applied.
  * 🔢 `num_commits`	: The number of recent commits to include in the review request.
  * 📦 `repo_name`	: The repository to use (linux, qemu, libvirt, ovmf).
  * 📂 `[dir_path]`	: (Optional) Path to a directory containing the commits.
  * 🔍 `[--check-diffs]`: (Optional) Check diffs between upstream and backport patches.
  * ❓ `[--help]`	: Help
  * 🆚 `[--version]`	: Displays version.

## 📂 Output
Generates a `review_request.html` file in the current directory.

## 🛠️ Installation
Run the installer script to set up the tool:
```bash
./installer
```

## 👨‍💻 Author
`Name :` Hemanth Selam
`Email:` hemanth.selam@gmail.com

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
