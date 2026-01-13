import argparse
import os

from .download import download_gists
from .environment import set_environment_variable


def main():
    parser = argparse.ArgumentParser(
        description="Download specified user's all gists at once"
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        metavar="Username",
        help="Github username to download gists from.",
    )
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        metavar="Token",
        help="Github public access token if you want to also download private gists.",
    )
    parser.add_argument(
        "-e",
        "--environment",
        action="store_true",
        help="Whether to use environment variables or not.",
    )
    parser.add_argument(
        "-g",
        "--git",
        action="store_true",
        help="Whether to download with git or not. False by default since it's "
        "dependent on whether or not git is downloaded (and your ssh/gpg key). "
        "IF YOU TYPE ANYTHING IN AFTER -g/--git IT WILL BE ACCEPTED AS TRUE.",
    )
    parser.add_argument(
        "-gu",
        "--gusername",
        type=str,
        metavar="Username",
        help="Set Github username as environment variable.",
    )
    parser.add_argument(
        "-gpat",
        "--gpat",
        type=str,
        metavar="Token",
        help="Set Github personal access token as environment variable.",
    )

    args = parser.parse_args()

    if args.gusername:
        set_environment_variable("GITHUB_USERNAME", args.gusername)
    if args.gpat:
        set_environment_variable("GITHUB_PERSONAL_ACCESS_TOKEN", args.gpat)
    if not args.gusername and not args.gpat:
        if args.environment:  # false by default/if you don't use the argument
            username = os.getenv("GITHUB_USERNAME")
            token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        else:
            username = args.username
            token = args.token

        git_check = args.git  # false by default/if you don't use the argument

        if not username:
            print("Pass your Github username with -u.")
        else:
            download_gists(username, token, git_check)


if __name__ == "__main__":
    main()
