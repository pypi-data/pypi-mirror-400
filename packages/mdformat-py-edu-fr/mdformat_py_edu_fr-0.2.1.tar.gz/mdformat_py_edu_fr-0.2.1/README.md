# Tiny wrapper around mdformat for the py-edu-fr project

We needed a specific markdown formatter for the
[py-edu-fr project](https://python-cnrs.netlify.app/edu).

mdformat-py-edu-fr is based on mdformat, mdformat-myst and Jupytext.

```
$ mdformat-py-edu-fr -h
usage: mdformat-py-edu-fr [-h] [--version] [--check] [--exclude PATTERN] [--verbose] [paths ...]

Format Markdown files for py-edu-fr project

positional arguments:
  paths                 Files or directories to format (if omitted, reads from stdin)

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --check               Check if files are formatted without modifying them (exit code 1 if changes needed)
  --exclude PATTERN     Glob pattern to exclude files/directories (can be specified multiple times)
  --verbose, -v         Print detailed information about processing
```
