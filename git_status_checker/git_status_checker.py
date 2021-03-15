#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    Copyright 2015 Rasmus Scholer Sorensen, rasmusscholer@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#

# pylint: disable=C0103

"""

Check git repositories for uncommitted changes and sync status with origin.


Inspired by:
* github.com/TomHodson/Git-Status-Notifier
* github.com/natemara/git_check
* github.com/yonchu/git-check

Python git bindings (not used, but still worth mentioning):
* pypi.python.org/pypi/GitPython
* github.com/libgit2/pygit2


Git status and --porcelain documentation:
* https://github.com/git/git/blob/master/Documentation/git-status.txt

"""


import sys
import os
import re
import yaml
import glob
import shlex
import argparse
import subprocess
from fnmatch import fnmatch
# from collections import defaultdict
# from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)


def parse_args(argv=None):
    """Parse command line arguments.

    Args:
        argv: list of command line arguments, e.g. sys.argv (default).

    Returns:
        parser and parsed args namespace (two-tuple).

    """

    parser = argparse.ArgumentParser(
        prog="git-status-checker",
        description="Git status checker script."
    )
    parser.add_argument("--verbose", "-v", action="count", help="Increase verbosity.")
    parser.add_argument("--testing", action="store_true", help="Run app in simple test mode.")
    parser.add_argument("--loglevel", default=logging.WARNING, help="Set logging output threshold level.")
    # parser.add_argument("--profile", "-p", action="store_true", help="Profile app execution.")
    # parser.add_argument("--print-profile", "-P", action="store_true", help="Print profiling statistics.")
    # parser.add_argument("--profile-outputfn", default="scaffold_rotation.profile",
    #                     help="Save profiling statistics to this file.")

    parser.add_argument("--recursive", action="store_true",
                        help="Scan the given basedirs recursively. This is the default.")
    parser.add_argument("--no-recursive", action="store_false", dest="recursive",
                        help="Disable recursive scanning. This implies that all the given basedirs are git "
                             "repositories, since sub-directories are not traversed.")

    parser.add_argument("--followlinks", action="store_true",
                        help="Follow symbolic links when walking/scanning the basedirs.")
    parser.add_argument("--no-followlinks", action="store_false", dest="followlinks")

    parser.add_argument("--ignore-untracked", action="store_true", help="Ignore untracked files.")

    parser.add_argument(
        "--no-check-remote-tracking-branch",
        dest="check_remote_tracking_branch",
        action="store_false", default=True,
        help=("Do not check if remote tracking branches have been configured for the currently checked-out worktree. "
              "Default is to report missing remote tracking branches, "
              "to ensure that a all work is committed and pushed.")
    )

    parser.add_argument("--check-fetch", action="store_true",
                        help="Check if origin has changes that can be fetched. This is disabled by default, since "
                        "it requires making a lot of remote requests which could be expensive.")

    parser.add_argument("--wait", action="store_true",
                        help="If changes are found, wait for input before continuing. This is typically used to "
                        "prevent the command prompt from closing when executing as e.g. a scheduled task.")

    parser.add_argument("--config", "-c",
                        help="Instead of providing command line arguments at the command line, "
                        "you can write arguments in a yaml file (as a dictionary).")

    parser.add_argument("--dirfile", "-f", nargs="+",
                        help="Instead of listing basedirs on the command line, you can list them in a file.")

    parser.add_argument("--ignorefile",  # nargs="+",
                        help="File with directories to ignore (glob patterns). "
                             "Note: Basedirs are NEVER ignored by glob patterns in the ignorefile, "
                             "the exclusion only appplies to sub-directories a given basedir.")

    parser.add_argument("basedirs", nargs="*", metavar="basedir",
                        help="One or more base directories to scan. A directory can be either a git repository, "
                        "or a directory containing one or more git repositories. "
                        "Basically it just scans recursively, considering all directories with a "
                        "'.git' subfolder a git repository. If no basedirs are given, "
                        "the current working directory is used.")

    return parser, parser.parse_args(argv)


def process_args(argns=None, argv=None):
    """ Process command line args and return a dict with args.

    If argns is given, this is used for processing.
    If argns is not given (or None), parse_args() is called
    in order to obtain a Namespace for the command line arguments.

    Will expand the entry "basedirs" using glob matching, and print a
    warning if a pattern does not match any files at all.

    If argns (given or obtained) contains a "config" attribute,
    this is interpreted as being the filename of a config file (in yaml format),
    which is loaded and merged with the args.

    Returns a dict.
    """
    if argns is None:
        _, argns = parse_args(argv)
    args = argns.__dict__.copy()

    # Load config with parameters:
    if args.get("config"):
        with open(args["config"]) as fp:
            cfg = yaml.load(fp)
        args.update(cfg)

    if args.get("loglevel"):
        try:
            args["loglevel"] = int(args.get("loglevel"))
        except ValueError:
            args["loglevel"] = getattr(logging, args["loglevel"])

    # On windows, we have to expand glob patterns manually:
    file_pattern_matches = [(pattern, glob.glob(os.path.expanduser(pattern))) for pattern in args['basedirs']]
    for pattern in (pattern for pattern, res in file_pattern_matches if len(res) == 0):
        print("WARNING: File/pattern '%s' does not match any files." % pattern)
    args['basedirs'] = [fname for pattern, res in file_pattern_matches for fname in res]

    if args.get("ignorefile"):
        args['ignorefile'] = os.path.expanduser(args['ignorefile'])

    return args


def read_ignorefile(ignorefile):
    """ Read file with glob patterns specifying files to ignore. """
    if ignorefile is None:
        if os.path.isfile(".git_checker_ignore"):
            logger.debug("ignorefile is None, using .git_checker_ignore in current working directory.")
            ignorefile = ".git_checker_ignore"
        else:
            logger.debug("ignorefile is None, returning empty list")
            return []
    logger.debug("Reading ignoreglobs from %s", ignorefile)
    with open(ignorefile) as fp:
        ignoreglobs = [line.strip() for line in fp if line.strip()]
    logger.debug("ignoreglobs: %s", ignoreglobs)
    return ignoreglobs


def read_basedirfiles(basedirfiles):
    """  Read one or more basedir files and return combined list of basedirs.
    Each basedirfile has a list of base directories to start from.
    """
    basedirs = []
    for basedirfile in basedirfiles:
        with open(basedirfile) as fp:
            basedirs += [line.strip() for line in fp if line.strip()]
    return basedirs


def is_git_workdir_or_repo(dirpath, dirnames, filenames):
    """ Returns 1 if dirpath is a git repository, 2 if dirpath is a git workdir, and 0 otherwise.
    (based solely on the directories and files in the directory).

    Args:
        dirpath: Directory (path).
        dirnames: List of child directory names within `dirpath` (just the names - not the path).
        filenames: List of file names within `dirpath` (just the names - not the path).

    Returns:
        True if dirpath is a git working directory (has a `.git` file or directory)
        or if dirpath is a git repository (has `config`, `HEAD`, `index` files).

    The equivalent `git` command is:
        git rev-parse --is-inside-git-dir || git rev-parse --is-inside-work-tree

    """
    if ".git" in dirnames or ".git" in filenames:
        # A git working directory can be linked with an external git repository, linked with a `.git` text file.
        return 2
    if "HEAD" in filenames and "config" in filenames and "refs" in dirnames:
        return 1
    return 0


def scan_gitrepos(basedirs, ignoreglobs=None, followlinks=False):
    """ Scan the list of basedirs for git repositories, traversing each basedir recursively.
    """
    if ignoreglobs is None:
        ignoreglobs = []
    if isinstance(basedirs, str):
        basedirs = [basedirs]
    gitrepos = []
    # first = 5  # True
    for basedir in basedirs:
        basedir_gitrepos = []  # make a list for each basedir (to see if any basedir are void of git repos)
        logger.debug("Walking basedir %s", basedir)
        for dirpath, dirnames, filenames in os.walk(basedir, followlinks=followlinks):
            # if first and first > 0:
            #    print("dirpath, dirnames, filenames) =", (dirpath, dirnames, filenames))
            #    first -= 1
            ignoredirs = [dirname for dirname in dirnames if any(fnmatch(dirname, pat) for pat in ignoreglobs)]
            if ignoredirs:
                logger.debug("Ignoring the following directories in %s: %s", dirpath, ignoredirs)
            for dirname in ignoredirs:
                dirnames.remove(dirname)
            # if ".git" in dirnames or ".git" in filenames:
            if is_git_workdir_or_repo(dirpath, dirnames, filenames):
                logger.debug("Git repository found: %s", dirpath)
                # Add git repo dir to list of repos and abort further recursion by emptying the dirnames list:
                basedir_gitrepos.append(dirpath)
                del dirnames[:]
        logger.info("%s git repositories found for basedir %s", len(basedir_gitrepos), basedir)
        gitrepos += basedir_gitrepos
    logger.info("%s git repositories found for all (%s) basedirs", len(gitrepos), len(basedirs))
    return gitrepos


def check_repo_status(gitrepo, fetch=False, ignore_untracked=False, check_remote_tracking_branch=True):
    """
    Checks the status of git repository <gitrepo> and returns a tuple of
        (commit-status, push-status, fetch-status)
    where commit status informs whether there are outstanding files not committed,
    push-status informs whether the repository is ahead of origin,
    and pull-status whether the repo is behind origin.
    If an element is boolean True, it means there are something to do (e.g. changes to commit).
    If all elements are boolean False, there are nothing to commit, push or fetch.
    """
    git_status_command = shlex.split("git status --porcelain=v1 --branch")
    try:
        status_output = subprocess.check_output(git_status_command, cwd=gitrepo)\
                                  .decode().strip().split("\n")
    except subprocess.CalledProcessError as e:
        print("Warning: failed to git status on %s: %s", gitrepo, e)
        return None, None, None
    #             False if "up-to-date" in status_output else status_output:
    # Examples of `git status` output:  (The first line is "on branch <branch>" or similar)
    #   Your branch is up-to-date with 'origin/master'.
    #   Your branch is ahead of 'origin/master' by 2 commits.
    #   nothing to commit, working tree clean   # If no remote tracking branch
    #   Changes not staged for commit           # No remote tracking branch, but local changes.
    # Examples of `git status --porcelain=v1 --branch` output (first line):
    #   ## devlegacy-rs                         # If no remote tracking branch.
    #   ## master...origin/master [ahead 1]     # Local master is 1 commit ahead of remote tracking branch.
    #   ## edge...origin/edge                   # Local branch is up to date with origin.
    #   ## HEAD (no branch)                     # Working with detached head.
    # status_regex = r"Your branch is (?P<status>.* (with|of)) (?P<branch>\'\w+\/\w+\') ?(?P<offset>.*)"
    # status_regex = (r"## (?P<local_branch>[0-9a-zA-Z_-]+)(\.\.\."
    #                 r"((?P<remote>[0-9a-zA-Z_-]+)/)?(?P<remote_branch>[0-9a-zA-Z_-]+)( ?\[(?P<ahead_behind>.+)\])?)?")
    status_regex = (
        r"## ((?P<commitish>\w+ \(no branch\))"
        r"|(?P<local_branch>[0-9a-zA-Z_-]+)"
        r"(\.\.\.((?P<remote>[0-9a-zA-Z_-]+)/)?(?P<remote_branch>[0-9a-zA-Z_-]+)( ?\[(?P<ahead_behind>.+)\])?)?)"
    )
    push_match = re.match(status_regex, status_output[0])
    logger.debug("%s git status output is: %s", gitrepo, status_output)
    if push_match:
        # Set push_status to False if there is nothing to push.
        # OBS: git status output changed from "up-to-date" to "up to date". Maybe use an external package?
        # Alternatively, use `git status --porcelain=v1 --branch` instead of just `git status`?
        local_commitish = push_match.group('commitish')  # If not working on a local branch
        local_branch = push_match.group('local_branch')
        push_remote = push_match.group('remote')
        remote_branch = push_match.group('remote')
        ahead_behind = push_match.group('ahead_behind')
        if push_remote is None:
            if check_remote_tracking_branch:
                push_status = "No remote tracking branch configured, working on local-only branch %r" % (local_branch,)
            else:
                push_status = False
        else:
            push_status = False if ahead_behind is None else "%s is %s of remote branch %s/%s" % (
                local_branch, ahead_behind, push_remote, remote_branch
            )
        # push_status = False if ("up-to-date" in push_status_str
        #                         or "up to date" in push_status_str) else status_output[1]
    else:
        print("OBS: %s status-line '%s' did not match status regex." % (gitrepo, status_output[1]), file=sys.stderr)
        logger.info("%s status[1] did not match standard status regex: %s", gitrepo, status_output[1])
        push_status = 'Error: git status output "%s" not recognized.' % (status_output[0])

    # Alternatively, compare hashes: (github.com/natemara/git_check)
    # local_hash=`git rev-parse --verify master`
    # remote_hash=`git rev-parse --verify origin/master`

    # Check for changed files commits:
    files_status = [line for line in status_output[1:] if line.strip()]
    if ignore_untracked:
        logger.debug("Removing lines for untracked files: %s", [line for line in files_status if line[1] == "?"])
        files_status = [line for line in files_status if line[1] != "?"]

    # Check for incoming changes (from whatever is the branch's default upstream):
    if fetch:
        # print("Checking fetch status for repo:", gitrepo, "...")
        try:
            fetch_dryrun = subprocess.check_output(
                ["git", "fetch", "--dry-run"],
                cwd=gitrepo,
                stderr=subprocess.STDOUT,  # redirect stderr to stdout to capture stderr with stdout.
            ).decode().strip()
            # proc = subprocess.run("git fetch --dry-run", capture_output=True)  # Alternative.
        except subprocess.CalledProcessError as exc:
            # print(f" - ERROR while checking fetch for repo {gitrepo}:", file=sys.stderr)
            # print(f" - ERROR: {exc}.", file=sys.stderr)
            # print(f" - Perhaps you do not have read access to the remote repository?", file=sys.stderr)
            # print(f" - Try to see if you can invoke `git fetch` manually in this repository.", file=sys.stderr)
            fetch_dryrun = str(exc) + " Maybe failed auth? Please do a manual `git fetch` to debug the issue."
        # print("fetch_dryrun:", fetch_dryrun)  # debug print
    else:
        fetch_dryrun = None
    logger.debug("%s: (%s, %s, %s)", gitrepo, len(files_status), push_status,
                 fetch_dryrun and len(fetch_dryrun))
    return files_status, push_status, fetch_dryrun


def print_report(gitrepo, commitstat, pushstat, fetchstat):
    print("\n"+gitrepo, "has outstanding", ", ".join(
            elem for elem in (commitstat and "commits", pushstat and "pushes", fetchstat and "fetches") if elem), ":")
    if pushstat:
        print("--", pushstat)
    if fetchstat:
        print("Outstanding fetches from origin:", fetchstat)
    if commitstat:
        print("-- outstanding commits: --")
        print("\n".join(commitstat))


def main(argv=None):
    """ Main driver """
    args = process_args(None, argv)
    logging.basicConfig(level=args.get("loglevel", logging.DEBUG),
                        format="%(asctime)s %(levelname)-5s %(name)12s:%(lineno)-4s%(funcName)16s() %(message)s")
    if args['basedirs'] is None:
        args['basedirs'] = []
    if args['dirfile']:
        args['basedirs'] += read_basedirfiles(args['dirfile'])
    logger.debug("Scanning %s basedirs", len(args['basedirs']))

    ignoreglobs = read_ignorefile(args['ignorefile'])

    if not args['basedirs']:
        logger.info("Using current directory as basedir: %s", os.path.abspath("."))
        args['basedirs'] = ["."]
    print("Basedirs:", ", ".join(os.path.abspath(path) for path in args['basedirs']))
    exit_status = 0     # exit 0 = "No dirty repositories."

    gitrepos = scan_gitrepos(args['basedirs'], ignoreglobs=ignoreglobs,
                             followlinks=args.get("followlinks", False))

    if not gitrepos:
        print("No git repositories found!")
        sys.exit(127)   # exit 127 = "Error: No repositories found."

    for gitrepo in gitrepos:
        if args.get('verbose', 0) > 0:
            print(f'Checking git repository: {gitrepo}   ['
                  f'fetch={args.get("check_fetch", False)}, '
                  f'ignore_untracked={args.get("ignore_untracked")}, '
                  f'check_remote_tracking_branch={args.get("check_remote_tracking_branch")}]'
            )
        commitstat, pushstat, fetchstat = status_tup = check_repo_status(
            gitrepo, fetch=args.get("check_fetch", False),
            ignore_untracked=args.get("ignore_untracked"),
            check_remote_tracking_branch=args.get("check_remote_tracking_branch", True)
        )
        if any(status_tup):
            print_report(gitrepo, commitstat, pushstat, fetchstat)
            exit_status = 1  # exit 1 = "dirty repositories found."
        elif args.get('verbose', 0) > 0:
            print(" - No updates found.")
    if exit_status > 0 and args.get('wait'):
        input("\nPress Enter to continue... ")
    sys.exit(exit_status)


def test():
    """ Primitive test. """
    logging.basicConfig(level=10,  # , style="{")
                        format="%(asctime)s %(levelname)-5s %(name)20s:%(lineno)-4s%(funcName)20s() %(message)s")
    testbasedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # package root dir
    ignorefile = os.path.join(testbasedir, "test", "testfiles", "ignore.txt")
    testbasedir = os.path.dirname(testbasedir)  # go up one level, to the folder that contains this project.
    testbasedir = os.path.join(testbasedir, "SublimeText_plugins")
    argv = [testbasedir, "--ignorefile", ignorefile] + sys.argv[2:]
    print("test argv:", argv)
    main(argv)


if __name__ == '__main__':
    if "--test" in sys.argv:
        test()
    else:
        main()
