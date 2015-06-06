#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##    Copyright 2015 Rasmus Scholer Sorensen, rasmusscholer@gmail.com
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##

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

"""





import sys
import os
import re
import yaml
import glob
import argparse
import subprocess
from collections import defaultdict
import logging
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta





def parse_args(argv=None):
    """
    Parse command line arguments.
    """

    parser = argparse.ArgumentParser(description="Git status checker script.")
    parser.add_argument("--verbose", "-v", action="count", help="Increase verbosity.")
    parser.add_argument("--testing", action="store_true", help="Run app in simple test mode.")
    parser.add_argument("--loglevel", default=logging.WARNING, help="Run app in simple test mode.")
    #parser.add_argument("--profile", "-p", action="store_true", help="Profile app execution.")
    #parser.add_argument("--print-profile", "-P", action="store_true", help="Print profiling statistics.")
    #parser.add_argument("--profile-outputfn", default="scaffold_rotation.profile",
                        #help="Save profiling statistics to this file.")

    parser.add_argument("--recursive", action="store_true",
                        help="Scan the given basedirs recursively. This is the default.")

    parser.add_argument("--no-recursive", action="store_false", dest="recursive",
                        help="Disable recursive scanning. Any 'basedir' must be a git repository.")
    parser.add_argument("--followlinks", action="store_true",
                        help="Follow symbolic links when walking/scanning the basedirs.")
    parser.add_argument("--no-followlinks", action="store_false", dest="followlinks")

    parser.add_argument("--ignore-untracked", action="store_true", help="Ignore untracked files.")

    parser.add_argument("--check-fetch", action="store_true",
                        help="Check if origin has changes that can be fetched. This is disabled by default, since "
                        "it requires making a lot of remote requests which could be expensive.")

    parser.add_argument("--config", "-c",
                        help="Instead of providing command line arguments at the command line, "
                        "you can write arguments in a yaml file (as a dictionary).")

    parser.add_argument("--dirfile", "-f", nargs="+",
                        help="Instead of listing basedirs on the command line, you can list them in a file.")

    parser.add_argument("--ignorefile", #nargs="+",
                        help="File with directories to ignore (glob patterns). "
                        "Note: Basedirs are NEVER ignored by glob patterns in ignorefile.")

    parser.add_argument("basedirs", nargs="*", metavar="basedir",
                        help="One or more base directories to scan. A directory can be either (a) a git repository, "
                        "or (b) a directory containing one or more git repositories. "
                        "Basically it just scans recursively, considering all directories with a "
                        "'.git' subfolder a git repository.")


    return parser, parser.parse_args(argv)


def process_args(argns=None, argv=None):
    """
    Process command line args and return a dict with args.

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
    """
    """
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
    """
    """
    basedirs = []
    for basedirfile in basedirfiles:
        with open(basedirfile) as fp:
            basedirs += [line.strip() for line in fp if line.strip()]
    return basedirs

from fnmatch import fnmatch

def scan_gitrepos(basedirs, ignoreglobs=None, followlinks=False):
    """
    """
    if ignoreglobs is None:
        ignoreglobs = []
    if isinstance(basedirs, str):
        basedirs = [basedirs]
    gitrepos = []
    #first = 5 # True
    for basedir in basedirs:
        basedir_gitrepos = [] # make a list for each basedir (to see if any basedir are void of git repos)
        logger.debug("Walking basedir %s", basedir)
        for dirpath, dirnames, _ in os.walk(basedir, followlinks=followlinks):
            #if first and first > 0:
            #    #print("First dirpath:", dirpath)
            #    #print("First dirpath:", dirpath)
            #    print("dirpath, dirnames, filenames) =", (dirpath, dirnames, filenames))
            #    #print("- ignoreglobs:", ignoreglobs)
            #    #first = False
            #    first -= 1
            ignore = [dirname for dirname in dirnames if any(fnmatch(dirname, pat) for pat in ignoreglobs)]
            if ignore:
                logger.debug("Ignoring files in %s: %s", dirpath, ignore)
            for dirname in ignore:
                dirnames.remove(dirname)
            if ".git" in dirnames:
                # we have a git repository, abort further recursion by emptying the dirnames list:
                del dirnames[:]
                logger.debug("Git repository found: %s", dirpath)
                basedir_gitrepos.append(dirpath)
        logger.info("%s git repositories found for basedir %s", len(basedir_gitrepos), basedir)
        gitrepos += basedir_gitrepos
    logger.info("%s git repositories found for all (%s) basedirs", len(gitrepos), len(basedirs))
    return gitrepos

def check_repo_status(gitrepo, fetch=False, ignore_untracked=False):
    """
    Checks the status of git repository <gitrepo> and returns a tuple of
        (commit-status, push-status, fetch-status)
    where commit status informs whether there are outstanding files not committed,
    push-status informs whether the repository is ahead of origin,
    and pull-status whether the repo is behind origin.
    If an element is boolean True, it means there are something to do (e.g. changes to commit).
    If all elements are boolean False, there are nothing to commit, push or fetch.
    """
    try:
        status_output = subprocess.check_output(["git", "status"], cwd=gitrepo)\
                                  .decode().strip().split("\n")
    except subprocess.CalledProcessError as e:
        print("Warning: failed to git status on %s: %s", gitrepo, e)
        return (None, None, None)
    #             False if "up-to-date" in status_output else status_output:
    # Examples:
    # Your branch is up-to-date with 'origin/master'.
    # Your branch is ahead of 'origin/master' by 2 commits.
    # OR NO INFO, if branch does not have any upstream set.
    # Changes not staged for commit:  ()
    status_regex = r"Your branch is (?P<status>.* (with|of)) (?P<branch>\'\w+\/\w+\') ?(?P<offset>.*)"
    push_match = re.match(status_regex, status_output[1])
    if push_match:
        push_status = status_output[1] if "up-to-date" not in push_match.group('status') else False
    else:
        logger.debug("%s status[1] did not match standard status regex: %s", gitrepo, status_output[1])
        push_status = push_match

    ## Alternatively, compare hashes: (github.com/natemara/git_check)
    # local_hash=`git rev-parse --verify master`
    # remote_hash=`git rev-parse --verify origin/master`

    ## Check for outstanding commits:
    status_porcelain = subprocess.check_output(["git", "status", "--porcelain"], cwd=gitrepo)\
                                 .decode().split("\n")
    status_porcelain = [line for line in status_porcelain if line.strip()]
    if ignore_untracked:
        logger.debug("Removing lines for untracked files: %s", [line for line in status_porcelain if line[1] == "?"])
        status_porcelain = [line for line in status_porcelain if line[1] != "?"]

    ## Check for incoming changes (from whatever is the branch's default upstream):
    if fetch:
        fetch_dryrun = subprocess.check_output(["git", "fetch", "--dry-run"], cwd=gitrepo)\
                                 .decode().strip()
    else:
        fetch_dryrun = None
    logger.debug("%s: (%s, %s, %s)", gitrepo, len(status_porcelain), push_status,
                 fetch_dryrun and len(fetch_dryrun))
    return (status_porcelain, push_status, fetch_dryrun)

def print_report(gitrepo, commitstat, pushstat, fetchstat):
    print("\n"+gitrepo, "has outstanding",
          ", ".join(elem for elem in (commitstat and "commits", pushstat and "pushes", fetchstat and "fetches") if elem),
          ":")
    if pushstat:
        #print(gitrepo, ":", pushstat)
        print("--", pushstat)
    if fetchstat:
        print("Outstanding fetches from origin:", fetchstat)
    if commitstat:
        print("-- outstanding commits: --")
        print("\n".join(commitstat))


def main(argv=None):
    """ Main driver """
    args = process_args(None, argv)
    logging.basicConfig(level=args.get("loglevel", 30),
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
    exit_status = 0     # exit 0 = "No dirty repositories."

    gitrepos = scan_gitrepos(args['basedirs'], ignoreglobs=ignoreglobs,
                             followlinks=args.get("followlinks", False))

    if not gitrepos:
        print("No git repositories found!")
        sys.exit(127)   # exit 127 = "Error: No repositories found."

    for gitrepo in gitrepos:
        (commitstat, pushstat, fetchstat) = status_tup = \
            check_repo_status(gitrepo,
                              fetch=args.get("check_fetch", False),
                              ignore_untracked=args.get("ignore_untracked"))
        if any(status_tup):
            print_report(gitrepo, commitstat, pushstat, fetchstat)
            exit_status = 1 # exit 1 = "dirty repositories found."
    sys.exit(exit_status)

def test():
    """ Primitive test. """
    logging.basicConfig(level=10,  #, style="{")
                        format="%(asctime)s %(levelname)-5s %(name)20s:%(lineno)-4s%(funcName)20s() %(message)s")
    testbasedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # package root dir
    ignorefile = os.path.join(testbasedir, "test", "testfiles", "ignore.txt")
    testbasedir = os.path.dirname(testbasedir) # go up one level, to the folder that contains this project.
    testbasedir = os.path.join(testbasedir, "SublimeText_plugins")
    argv = [testbasedir, "--ignorefile", ignorefile] + sys.argv[2:]
    print("test argv:", argv)
    main(argv)

if __name__ == '__main__':
    if "--test" in sys.argv:
        test()
    else:
        main()
