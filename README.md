# git_status_checker
Yet another git status checker, in python. Because none of the bash-based ones were working on my Windows box with git-bash...


## What it does

This is just a script that
(1) finds git repositories given a list of base directories, and
(2) checks if any of the repositories have uncommitted changes or needs to be updated with origin, i.e. if it has changes that have not been pushed, or if origin has changes that have not been pulled.


## Recommended use:

1. Produce a list of places (base-dirs) where you have git repositories and save it to a file.
   It might look something like:
    ~/Dev/src-repos
    ~/Documents/Projects
    ~/Documents/Personal_stuff/My_project_A

2. Then run git_status_checker.py with:
    python git_status_checker.py -f <file-with-list-of-basedirs>

The script will walk each base-dir, searching for git repositories, then print the status for all
repositories with outstanding commits or that can be pushed or fetched to/from origin.

## Variations

The script provides for a range of choices on how you use it:
* You can provide base-dirs directly at the command line
* You can use multiple base-dirs-files.
* You can provide a --config file with command line args (if you don't want to specify them on the command line).
* You can use --no-recursive command line argument to disable recursive walking (it is then assumed that all "basedirs" are git repositories).
* You can use the --ignorefile argument to provide glob filters to exclude directories from scanning.
* If --ignorefile is not given but the current directory contains a file ".git_checker_ignore", this is used as ignorefile. (Similar to how git automatically ignores files in .gitignore).


## Notes:

The way I've set my stuf up is that I have a .git_checker_ignore in my main "repository" folder, ~/Dev/src-repos/, which lists all
non-git repositories/folders. (I have more git repositories than non-git folders, so this is easiest for me).
I then simply run:
    python <path to git_status_checker.py> --ignore-untracked ~/Dev/src-repos

Oh, and yes, you can use "~" and "*" to specify files, even on Windows.
