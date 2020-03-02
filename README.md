# git_status_checker
Yet another git status checker, in python. Because none of the bash-based ones were working on my Windows box with git-bash...


## What it does:

This is just a script that
(1) finds git repositories given a list of base directories, and
(2) checks if any of the repositories have uncommitted changes or needs to be updated with origin, i.e. if 
it has changes that have not been pushed, or if origin has changes that have not been pulled.


## Installation:

This script does not need to be "installed" *per se*. 
The only non-standard-library requirement is `pyyaml`, which is used to save script configuration files.

Just download the `git_status_checker.py` script (or clone the whole repository),
and run the script using whatever Python interpreter you have (Python 3+ only, no legacy python).



## Recommended use, examples:


### Basic usage:

Open your command prompt / terminal and navigate to where you keep your git repositories:

```
cd ~/Dev
```

Then simply run `git_status_checker.py`:

```
~/Dev>  python /path/to/git_status_checker.py
```

That's it. The `git_status_checker.py` script will look in all sub-folders, searching for
git repositories, and for every repository it finds, it will check to see if it has outstanding 
changes to be committed, or commits that have not been pushed to origin, 
and display the results in the terminal.


### Option 2: Using a file containing all the base-dirs

If your git repositories are scattered in multiple locations, you may want to create a file
containing each location, and then just load that file with `git_status_checker.py`.

1. Produce a list of places ("base-dirs") where you have git repositories and save it to a file.
   These are just "top level" folders, and might look something like:
    `~/Dev/src-repos`,
    `~/Documents/Projects`,
    `~/Documents/Personal_stuff/My_project_A`.

2. Then run git_status_checker.py with:
    python git_status_checker.py -f <file-with-list-of-basedirs>

The script will walk each base-dir, searching for git repositories, then print the status for all
repositories with outstanding commits or that can be pushed or fetched to/from origin.



### Running on a schedule, Windows:

It is convenient to run the `git_status_checker.py` script on a schedule, 
e.g. once a week or every afternnon,
and display a message if any uncommitted changes or outstanding commits where found.

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
8. Under "Start a Program", the Program/script should be the python interpreter
   and "Add arguments" should be the path to `git_status_checker.py`, and the arguments needed, e.g.:
   `%USERPROFILE%\Dev\git-status-checker\git_status_checker\git_status_checker.py --wait --ignore-untracked "%USERPROFILE%\Dev" "%USERPROFILE%\Documents\Projects"
    * OBS: It is a good idea to copy/paste the values you just entered above into a command prompt,
      and check that it runs coorectly.
9. On the "Finish" screen, review your scheduled task and press "Finish".
10. Test that your program works, by right-clicking your task and select "Run".
 

 



### Running in a batch script:

You can also run a batch script, 
which runs `git_status_checker.py` and pauses if any uncommitted or unpushed changes were found.

See batch script examples in the `bin/` folder.



## Variations

The script provides for a range of choices on how you use it:
* You can provide base-dirs directly at the command line
* You can use multiple base-dirs-files.
* You can provide a --config file with command line args (if you don't want to specify them on the command line).
* You can use --no-recursive command line argument to disable recursive walking (it is then assumed that all "basedirs" are git repositories).
* You can use the --ignorefile argument to provide glob filters to exclude directories from scanning.
* If --ignorefile is not given but the current directory contains a file ".git_checker_ignore", this is used as ignorefile. (Similar to how git automatically ignores files in .gitignore).


## Command line reference:

```
> python git-status-checker\git_status_checker\git_status_checker.py --help

usage: git_status_checker.py [-h] [--verbose] [--testing]
                             [--loglevel LOGLEVEL] [--recursive]
                             [--no-recursive] [--followlinks]
                             [--no-followlinks] [--ignore-untracked]
                             [--check-fetch] [--wait] [--config CONFIG]
                             [--dirfile DIRFILE [DIRFILE ...]]
                             [--ignorefile IGNOREFILE]
                             [basedir [basedir ...]]

Git status checker script.

positional arguments:
  basedir               One or more base directories to scan. A directory can
                        be either (a) a git repository, or (b) a directory
                        containing one or more git repositories. Basically it
                        just scans recursively, considering all directories
                        with a '.git' subfolder a git repository.

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         Increase verbosity.
  --testing             Run app in simple test mode.
  --loglevel LOGLEVEL   Set logging output threshold level.
  --recursive           Scan the given basedirs recursively. This is the
                        default.
  --no-recursive        Disable recursive scanning. Any 'basedir' must be a
                        git repository.
  --followlinks         Follow symbolic links when walking/scanning the
                        basedirs.
  --no-followlinks
  --ignore-untracked    Ignore untracked files.
  --check-fetch         Check if origin has changes that can be fetched. This
                        is disabled by default, since it requires making a lot
                        of remote requests which could be expensive.
  --wait                If changes are found, wait for input before
                        continuing. This is typically used to prevent the
                        command prompt from closing when executing as e.g. a
                        scheduled task.
  --config CONFIG, -c CONFIG
                        Instead of providing command line arguments at the
                        command line, you can write arguments in a yaml file
                        (as a dictionary).
  --dirfile DIRFILE [DIRFILE ...], -f DIRFILE [DIRFILE ...]
                        Instead of listing basedirs on the command line, you
                        can list them in a file.
  --ignorefile IGNOREFILE
                        File with directories to ignore (glob patterns). Note:
                        Basedirs are NEVER ignored by glob patterns in
                        ignorefile.


```



## Notes:

The way I've set my stuf up is that I have a .git_checker_ignore in my main "repository" folder, ~/Dev/src-repos/, which lists all
non-git repositories/folders. (I have more git repositories than non-git folders, so this is easiest for me).
I then simply run:
    python <path to git_status_checker.py> --ignore-untracked ~/Dev/src-repos

Oh, and yes, you can use "~" and "*" to specify files, even on Windows.
