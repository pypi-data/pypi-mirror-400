# gist-neko

CLI for downloading all gists from a specified user.

## Installation

### Via PyPI (Recommended)

```sh
pip install gist-neko
```

### From Source (Development)

```sh
git clone git@github.com:NecRaul/gist-neko.git
cd gist-neko
# You can skip the next two commands
# for installing it globally
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,build]
```

## Usage

`gist-neko` acts as a sync tool. If a gist folder doesn't exist, it clones it, if it does, it updates it.

```sh
# Download/Sync public gists with `requests`
gist-neko -u <github-username>

# Download/Sync public and private gists with `requests` (using a token)
gist-neko -u <github-username> -t <github-personal-access-token>

# Use 'git clone/pull' instead of 'requests' (preserves history, branches and submodules)
gist-neko -u <github-username> -g

# Use 'git' with a token for private gist syncing
gist-neko -u <github-username> -t <github-personal-access-token> -g
```

### Environment Variables

You can save your credentials to environment variables to avoid passing them manually in every command.

```sh
# Set your credentials as environment variables
gist-neko -gu <github-username> -gpat <github-personal-access-token>

# Run using the stored environment variables
gist-neko -e

# Run using environment variables with the git engine
gist-neko -e -g
```

> [!WARNING]
> The `-gu` and `-gpat` flags for setting environment variables only work on Windows.
>
> It is recommended to set `$GITHUB_USERNAME` and `$GITHUB_PERSONAL_ACCESS_TOKEN` variables in your shell profile.

### Options

```sh
-u, --username      USERNAME    GitHub username to download gists from
-t, --token         TOKEN       GitHub personal access token (required for private gists)
-e, --environment   -           Use stored environment variables for username and token
-g, --git           -           Use git engine instead of requests (handles history/branches/submodules)
-gu, --gusername    USERNAME    Save the GitHub username to your environment variables
-gpat, --gpat       TOKEN       Save the GitHub token to your environment variables
```

> [!TIP]
> The `-e` and `-g` flags are a boolean toggle.

## Dependencies

* [requests](https://github.com/psf/requests): fetch data from the GitHub API and handle downloads.

## How it works

The tool queries the `https://api.github.com/users/{username}/gists` endpoint. It retrieves public Gists when unauthenticated, or both public and private Gists when an authentication token is provided.

Once the gist list is retrieved, `gist-neko` automates the synchronization process using one of two engines:

* Requests Engine (Default): Fetches the gist as a compressed snapshot. This is fast but does not include **history**, **branches** or **submodules**.
* Git Engine (via `-g` or `--git` flag): Uses your local **git** installation to perform a full **clone** or **pull** This preserves the complete **history**, **branches** and **submodules**.

### The Manual Way

Without this tool, you would need to manually parse JSON responses, manage authentication headers, and write logic to differentiate between new clones and existing updates:

```sh
# A simplified version of the logic gist-neko automates
# It fetches the id and description, then loops through them
curl -s -H "Authorization: token $GITHUB_PERSONAL_ACCESS_TOKEN" https://api.github.com/users/NecRaul/gists |
    jq -r '.[] | "\(.description // .id) \(.id)"' | while read -r name id; do
    if [ ! -d "$name" ]; then
        git clone --recursive "git@gist.github.com:$id.git" "$name"
    else
        echo "Pulling '$name'..."
        git -C "$name" pull --recurse-submodules
    fi
done
```

### The gist-neko way

* Dynamic API Routing: Automatically identifies the correct GitHub endpoint. It uses `/users/{username}/gists` for browsing, ensuring that when authenticated, you get the full list of both public and private gists you have permission to view.
* State-Aware Syncing: Instead of a simple download, it checks your local file system using the gist's description or ID as the folder name. If a gist already exists, it intelligently switches to an "update" mode (using `git pull` or overwriting via `requests`) to keep your local mirror current.
* Hybrid Engine Support:
  * Lightweight Mode: Uses `requests` to pull gist snapshots quickly without needing `git` installed or **SSH keys** configured.
  * Developer Mode (`-g`): Interfaces directly with your local `git` binary to handle **full history**, **branch tracking**, and **submodule recursion**.
* Secure Credential Persistence: Rather than requiring you to paste tokens into every command, the `-gu` and `-gpat` flags securely interface with your environment variables, allowing for a clean, single-flag execution with `-e`.
* Subprocess Management: Uses `Python`'s `subprocess` and `os` modules to provide a robust bridge between the `GitHub API` and your local shell, handling directory navigation and command execution automatically.`
