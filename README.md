# 🚀 CommitChecker

CommitChecker is a script to check the versions of specific commits in various repositories. It supports parallel processing and can handle multiple repositories such as Linux, QEMU, Libvirt, and OVMF.

## ✨ Features

- 🕵️‍♂️ Detects if the current directory is a Git repository.
- 📂 Allows specifying the path of an existing stable repository or downloading it from GitHub.
- 🛠️ Supports multiple repositories: Linux, QEMU, Libvirt, and OVMF.
- 🔄 Fetches the latest tags and checks versions for specified commit IDs.
- 📄 Outputs the results in an HTML file.

## 📋 Usage

```bash
./commitchecker [-r <repository>] [--help] [--version]
```

## ⚙️ Options

* `-r <repository>`	: Specify the repository to use (linux, qemu, libvirt, ovmf).
* `--help`		: Display the help message.
* `--version`		: Display the version information.

## 📝 Instructions
1. 🌐 Ensure you have a stable internet connection.
2. 🏃 Run the script from a directory where you want to perform the operations.
3. ❓ If the current directory is not a Git repository, you will be prompted to either:
	* 📁 Enter the path of an existing stable repository.
	* ⬇️ Download the stable repository from GitHub.
4. 🛤️ If you choose to enter a path, ensure the path is correct and points to a valid Git repository.
5. 📥 If you choose to download, the repository will be cloned to your home directory.
6. 🗂️ After setting up the repository, you will be asked to provide commit IDs directly.
7. 📊 The script will check the versions for each commit ID and save the output as an HTML file in your home directory.

## 💡 Example
```bash
./commitchecker.sh -r linux
```

## 👤 Author
* `Hemanth Selam`

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🏷️ Version
CommitChecker version 1.0.0
