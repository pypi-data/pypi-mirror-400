# GitHub Simulation Shell

A feature-rich GitHub simulation shell that provides a command-line interface for GitHub operations.

## Features

### Repository Operations
- `repos` - List current user's repositories
- `repo <owner>/<repo>` - View specified repository information
- `issues <repo>` - View repository Issues
- `branches <repo>` - View repository branches
- `commits <repo>` - View recent repository commits
- `contributors <repo>` - View repository contributors
- `prs <repo>` - View repository Pull Requests
- `gists <username>` - View user's Gists

### Search Functionality
- `search <query>` - Search GitHub repositories

### Organization Operations
- `org <orgname>` - View specified organization information

### User Operations
- `user <username>` - View specified user information
- `followers` - View current user's followers
- `following` - View current user's following

### System Commands
- `help` - Display help information
- `clear` - Clear the screen
- `exit` - Exit the simulation shell
- `update` - Check and update to the latest version
- `version` - Display current version

## Installation

### Install from PyPI
```bash
pip install github-shell
```

### Install from Source
```bash
git clone https://github.com/wjr-2015/wjr-2015-github_shell.git
cd wjr-2015-github_shell
pip install -e .
```

## Usage

### Basic Usage
```bash
github-shell
```

### Command Examples
```bash
# List current user's repositories
github-shell:wjr-2015$ repos

# View specified repository information
github-shell:wjr-2015$ repo octocat/Hello-World

# Search repositories
github-shell:wjr-2015$ search python github

# Check for updates
github-shell:wjr-2015$ update
```

## Configuration

### Set GitHub Token
To access private repositories, you can set your GitHub token in the script:

```python
# Set in github_shell/config.py
TOKEN = "your_github_token"
```

## Auto Update

The script includes an auto-update feature. Run the `update` command to check and update to the latest version.

## Version History

- v1.1.0 - Added contributors view, PR view, Gists view, repository search, organization information view, etc.
- v1.0.0 - Initial version with basic repository and user operations

## License

MIT License
