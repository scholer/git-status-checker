# git-status-checker

Yet another git status checker, in python. 
Because none of the bash-based ones were working on my Windows box with git-bash...


## What it does:

This is just a script that
(1) finds git repositories given a list of base directories, and
(2) checks if any of the repositories have uncommitted changes or needs to be updated with origin, i.e. if 
it has changes that have not been pushed, or if origin has changes that have not been pulled.


## Installation:

You can install git-status-checker with pip:

```shell
> pip install git-status-checker
```

By default, this will get you the most recent release from PyPI.

If you want to use the most recent developer version from GitHub,
e.g. if you want to make changes to how git-status-checker works,
you can download or clone the git-status-checker repository, and then 
add a `-e` flag when installing with `pip` to install in "editable" mode:
`pip install -e git-status-checker`.


Installation is not strictly required, it is perfectly possible to use 
git-status-checker by running `git_status_checker.py` as a plain python script.
The only requirement is that you have `pyyaml` installed (is used to save script configuration files).
Just download the `git_status_checker.py` script (or clone the whole repository),
and run the script using whatever Python interpreter you have (Python 3+ only, no legacy python), e.g.:

```
> python /path/to/git-status-checker/git_status_checker/git_status_checker.py
```

However, the advantage of installing git-status-checker with pip is that you don't have
to remember where you placed the script, you can always just run it using
either `> python -m git_status_checker` or simply `> git-status-checker`.



## Recommended use, examples:


### Basic usage:

Open your command prompt / terminal and navigate to where you keep your git repositories, e.g.:

```
cd ~/Dev
```

If you have *installed* git-status-checker, you can then just type:

```
~/Dev>  python -m git_status_checker
```

Alternatively, if you have simply downloaded `git_status_checker`, then just
run `git_status_checker.py` as a python script:

```
~/Dev>  python /path/to/git_status_checker.py
```


That's it! `git-status-checker` will look in all sub-folders, searching for
git repositories, and for every repository it finds, it will check to see if it has outstanding 
changes to be committed, or commits that have not been pushed to origin, 
and display the results in the terminal.

* NOTE: Many of the examples below assumes git-status-checker is installed. 
If you are running `git_status_checker.py` as a script, rather than as an installed module,
just replace `python -m git_status_checker` with `python /path/to/git_status_checker.py`.

The installation process will also install `git-status-checker` as a directly-executable 
program, so instead of typing `python -m git_status_checker`, you can also type:

```
~/Dev>  git-status-checker
```


### Specifying directories to search for git repositories:

It is possible to tell git-status-checker where to search for git repositories,
just add the base directories as arguments:

```
> python -m git_status_checker ~/Dev ~/Documents
```

The script will walk each of the given directories (`~/Dev` and `~/Documents`) searching for git 
repositories, then print the status for all repositories with outstanding commits or that can be 
pushed or fetched to/from origin.

And yes, you can use "~" and "*" to specify files and folders, even on Windows.


### Using a file containing all the base-dirs

If you have a lot of git repositories scattered in multiple locations, you may want to create a file
containing each location, and then just load that file with `git_status_checker.py`,
instead of having to type all locations as arguments every time you run `git-status-checker`:

First, produce a list of places ("base-dirs") where you have git repositories and save it to a file.
These are just "top level" folders, and might look something like:

```
~/Dev/src-repos
~/Documents/Work-projects
~/Documents/Personal-projects
```

Then run git_status_checker.py with:

```
> python -m git_status_checker -f <file-with-list-of-basedirs>
```



### Running on a schedule, Windows:

It is convenient to run `git-status-checker` on a regular schedule, 
e.g. once a week or every afternoon, and display a message if any uncommitted changes 
or outstanding commits where found.

One way to do this in Windows is to use Task Scheduler to run `git_status_checker`. 
To do this:

1. Open Task Scheduler 
2. Optionally create a Task Library folder to store your own tasks in, 
so they are not mixed with all the other Task Scheduler tasks.
3. Select "Create Basic Task..." (e.g. from the "Action(s)" panel or menu item, or right-click the folder).
4. Under name, type something like "Git status checker of Dev and Projects folders", 
   and under description something like "Run git_status_checker.py script on ~/Dev and ~/Documents/Projects folders".
   (adapt name and description according to where your git repositories are located).
5. Under "Trigger", select "Daily" (or weekly, etc). You can adjust this afterwards.
6. Under the next tab, select when you would like the task to run.
7. Under "Action", select "Start a program".
8. Under "Start a Program", the Program/script should be the python interpreter to use, e.g. `python`,
   and "Add arguments" should be `-m git_status_checker` (to run git-status-checker), 
   followed by the git-status-checker arguments needed, e.g.:
   `-m git_status_checker --wait --ignore-untracked "~/Dev" "~/Documents/Projects"`
   to run git-status-checker for all git repositories inside `~/Dev` and `~/Documents/Projects`,
   ignoring untracked files. We add the `--wait` flag so the command prompt window will stay open 
   if outstanding commits or pushes are found. 
    * OBS: It is a good idea to copy/paste the values you just entered above into a command prompt,
      and check that git-status-checker runs correctly before saving your task.
9. On the "Finish" screen, review your scheduled task and press "Finish".
10. Test that your program works, by right-clicking your task and select "Run".






### Running in a batch script:

In some circumstances you may want to run `git_status_checker.py` from within batch script.

See batch script examples in the `examples/` folder.



## Variations

The script provides for a range of choices on how you use it:
* You can provide base-dirs directly at the command line
* You can use multiple base-dirs-files.
* You can provide a --config file with command line args (if you don't want to specify them on the command line).
* You can use --no-recursive command line argument to disable recursive walking (it is then assumed that all "basedirs" are git repositories).
* You can use the --ignorefile argument to provide glob filters to exclude directories from scanning.
* If --ignorefile is not given but the current directory contains a file ".git_checker_ignore", this is used as ignorefile. (Similar to how git automatically ignores files in .gitignore).


## Exit codes:

The program will exit with the following exit codes:

* `0` → Indicating that NO "dirty" repositories were found (repositories with outstanding 
  changes to be committed or commits to be pushed/pulled).
* `1` → Indicating that "dirty" repositories were found.
* Other exit codes indicates that there was an error running the program,
  e.g. bad arguments.


## Command line reference:

You can always run git-status-checker with the `--help` flag to see a quick reference on 
the various options and arguments that can be used with git-status-checker:

<!-- OBS: Set window width to 90 chars before running git-status-checker --help -->

```
> git-status-checker --help

usage: git-status-checker [-h] [--verbose] [--testing] [--loglevel LOGLEVEL]
                          [--recursive] [--no-recursive] [--followlinks]
                          [--no-followlinks] [--ignore-untracked]
                          [--no-check-remote-tracking-branch] [--check-fetch] [--wait]
                          [--config CONFIG] [--dirfile DIRFILE [DIRFILE ...]]
                          [--ignorefile IGNOREFILE]
                          [basedir [basedir ...]]

Git status checker script.

positional arguments:
  basedir               One or more base directories to scan. A directory can be either
                        a git repository, or a directory containing one or more git
                        repositories. Basically it just scans recursively, considering
                        all directories with a '.git' subfolder a git repository. If no
                        basedirs are given, the current working directory is used.

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         Increase verbosity.
  --testing             Run app in simple test mode.
  --loglevel LOGLEVEL   Set logging output threshold level.
  --recursive           Scan the given basedirs recursively. This is the default.
  --no-recursive        Disable recursive scanning. This implies that all the given
                        basedirs are git repositories, since sub-directories are not
                        traversed.
  --followlinks         Follow symbolic links when walking/scanning the basedirs.
  --no-followlinks
  --ignore-untracked    Ignore untracked files.
  --no-check-remote-tracking-branch
                        Do not check if remote tracking branches have been configured
                        for the currently checked-out worktree. Default is to report
                        missing remote tracking branches, to ensure that a all work is
                        committed and pushed.
  --check-fetch         Check if origin has changes that can be fetched. This is
                        disabled by default, since it requires making a lot of remote
                        requests which could be expensive.
  --wait                If changes are found, wait for input before continuing. This is
                        typically used to prevent the command prompt from closing when
                        executing as e.g. a scheduled task.
  --config CONFIG, -c CONFIG
                        Instead of providing command line arguments at the command line,
                        you can write arguments in a yaml file (as a dictionary).
  --dirfile DIRFILE [DIRFILE ...], -f DIRFILE [DIRFILE ...]
                        Instead of listing basedirs on the command line, you can list
                        them in a file.
  --ignorefile IGNOREFILE
                        File with directories to ignore (glob patterns). Note: Basedirs
                        are NEVER ignored by glob patterns in the ignorefile, the
                        exclusion only appplies to sub-directories a given basedir.
```
