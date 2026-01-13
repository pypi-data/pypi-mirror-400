import sys
import re
import time
import os
import argparse
import subprocess
import traceback
import copy
import logging
from pathlib import Path

from ktpanda import git_helper

from . import RepoWatcher

def setup_python_logging(verbose=False):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if verbose else logging.INFO)

    log_formatter = logging.Formatter('%(asctime)s %(levelname)s: [%(name)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root.addHandler(console_handler)

def main():
    p = argparse.ArgumentParser(description='')
    p.add_argument('repos', type=Path, nargs='*')
    p.add_argument('-l', '--repo-list', type=Path)
    p.add_argument('-v', '--verbose', action='store_true', help='')
    #p.add_argument(help='')
    args = p.parse_args()

    setup_python_logging(args.verbose)

    repo_paths = []
    repo_watchers = []
    for path in args.repos:
        repo_paths.append(path)

    if args.repo_list:
        base = args.repo_list.parent
        with args.repo_list.open() as fp:
            for line in fp:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                path = (base / line).absolute()
                repo_paths.append(path)

    for path in repo_paths:
        try:
            print(f'Initialzing watcher for {path} ...')
            repo_watchers.append(RepoWatcher(path))
        except Exception:
            print(f'Error initializing watcher for {path}', file=sys.stderr)
            traceback.print_exc()

    if not repo_watchers:
        print('No repositories defined', file=sys.stderr)
        return

    RepoWatcher.run(repo_watchers)

if __name__ == '__main__':
    main()
