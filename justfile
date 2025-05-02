# You can run these from any directory using the `-f <justfile>` argument, e.g.:
#   $ just -f /path/to/this/justfile uv-check-these `pwd`
# Note that absolute paths are required, since the commands will be executed from the
# folder containing this justfile.
# If you want more fancy-pansy, you can pip-install git-status-checker (or use `pipx` or `uvx`),
# and run from anywhere using
#   $ git-status-checker <basedirs>
# or
#   $ uvx git-status-checker
# etc.

# variadic param: '+' aceept one or more values
uv-check-these +BASEDIRS:
    uv run git_status_checker/git_status_checker.py {{BASEDIRS}}

uv-check-from-file DIRFILE:
    uv run git_status_checker/git_status_checker.py --dirfiel {{DIRFILE}}

