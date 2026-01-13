import sys
import re
import time
import os
import argparse
import subprocess
import traceback
import logging
import copy
from pathlib import Path

from ktpanda import git_helper

log = logging.getLogger(__name__)

EDITLOG_BRANCH = 'editlog'
EDITLOG_BASE_BRANCH = EDITLOG_BRANCH + '-base'

EXCLUDE_EXT = {'.3mf', '.stl', '.zip', '.jpg', '.jpeg', '.png'}

def gitdir_allow_trigger(relpath):
    if relpath == 'HEAD':
        return True

    if relpath.startswith('refs'):
        if relpath.startswith('refs/heads/editlog'):
            return False
        return True

    if relpath.startswith('info'):
        return True

    return False

class BaseRepoWatcher:
    def __init__(self, repo_path):
        self.git = git_helper.Git(repo_path)
        self.repo_path = self.git.get_toplevel()

        info = self.git.run_capt(['rev-parse', '--show-toplevel', '--git-dir']).split('\n')

        repo_path = self.repo_path = self.git.repo_path = Path(info[0]).absolute()
        git_dir = self.git_dir = (repo_path / info[1]).absolute()

        self.main_index = git_dir / 'index'
        self.main_index_lock = git_dir / 'index.lock'

        self.editlog_dir = git_dir / 'editlog'
        self.editlog_index = self.editlog_dir / 'index'
        self.editlog_head_file = self.editlog_dir / 'HEAD'

        self.git.env_vars['GIT_INDEX_FILE'] = str(self.editlog_index)

        self.git_with_editdir = copy.copy(self.git)
        self.git_with_editdir.env_vars = self.git.env_vars | {'GIT_DIR': str(self.editlog_dir)}

        self.do_not_log_if_exists = [
            git_dir / 'MERGE_HEAD',
            git_dir / 'rebase-apply',
            git_dir / 'rebase-merge',
        ]

        # self.trigger_ignore = {
        #     str(self.git_dir),
        #     str(self.editlog_dir),
        #     str(self.main_index_lock),
        # }

        self.last_check_event_time = 0
        self.last_event_time = 1
        self.deferred_check_time = None

        self.editlog_branch_head = get_branch(self.git, EDITLOG_BRANCH)
        self.last_head = get_branch(self.git, EDITLOG_BASE_BRANCH)

        if not self.editlog_branch_head:
            # Create an empty tree to start with
            empty_blob = self.git.run_capt(['hash-object', '-w', '-t', 'blob', '--stdin'], input=b'')
            tree_data = f'100644 .gitkeep\0'.encode('ascii') + bytes.fromhex(empty_blob.strip())
            self.editlog_tree = self.git.run_capt(['hash-object', '-w', '-t', 'tree', '--stdin'], input=tree_data)
            self.editlog_branch_head = self.git.run_capt(['commit-tree', self.editlog_tree, '-m', 'Empty initial editlog commit'])
            self.git.run_capt(['branch', '-f', EDITLOG_BRANCH, self.editlog_branch_head])
        else:
            self.editlog_tree = self.git.run_capt(['log', '-n', '1', '--format=%T', self.editlog_branch_head])

        self.setup_editlog_dir()

    def setup_editlog_dir(self):
        dir = self.editlog_dir
        dir.mkdir(exist_ok=True)

        if not (f := dir / 'commondir').exists():
            f.write_text('..\n')

        if not (f := dir / 'HEAD').exists():
            current_head = self.git.run_capt(['rev-parse', '--verify', 'HEAD'])
            f.write_text(current_head + '\n')

    def path_modified(self, path):
        try:
            # ignore all paths under gitdir except specific files
            relpath = path.relative_to(self.git_dir)
            if not gitdir_allow_trigger(str(relpath)):
                return False
        except ValueError: # path is not relative to gitdir
            pass

        self.last_event_time = time.time()
        return True

    def should_check(self):
        event_time = self.last_event_time
        if self.last_check_event_time == event_time:
            return False

        ctime = time.time()
        time_since_last_event = ctime - event_time

        # Wait for idle of at least 3 seconds before checking
        if time_since_last_event < 3:
            # If this is the first time we've seen an event since the last check, note
            # the time and return False.
            if self.deferred_check_time is None:
                self.deferred_check_time = event_time
                return False

            # If it's been less than 30 seconds after the first deferred check, return False.
            # Otherwise, continue and force a check.
            if ctime < self.deferred_check_time + 30:
                return False

        self.last_check_event_time = event_time
        return True

    def check(self):
        if self.main_index_lock.exists():
            return

        if not self.should_check():
            return

        print()
        print(f'{self.repo_path}: possible changes detected, checking git...')


        if any(f.exists() for f in self.do_not_log_if_exists):
            print(f'{self.repo_path}: rebase/merge in progress, not logging')
            return

        current_head = self.git.run_capt(['rev-parse', '--verify', 'HEAD'])

        # Force our head to be the head of the editlog branch so git status won't try to
        # read the actual head
        self.editlog_head_file.write_text(self.editlog_branch_head + '\n')

        # reset our index to editlog head
        self.git_with_editdir.run(['reset'])

        changes = self.git_with_editdir.status(['--untracked=all', '--ignored=traditional', '--no-renames'])

        add_files = []
        delete_files = []
        for relpath, statidx, stattree, renfrom in changes:
            is_excluded = Path(relpath).suffix.lower() in EXCLUDE_EXT
            if is_excluded:
                # If file is excluded, but is not untracked, excluded, or staged for deletion,
                # then force a deletion.
                if stattree not in {'D', '?', '!'}:
                    delete_files.append(relpath)
            else:
                if stattree not in {'!'}:
                    add_files.append(relpath)


        if add_files:
            input = '\0'.join(add_files)
            self.git_with_editdir.run_capt(['add', '-f', '--pathspec-from-file=-', '--pathspec-file-nul'], input=input)

        if delete_files:
            input = ''.join(f'0 0000000000000000000000000000000000000000\t{path}\0' for path in delete_files)
            self.git_with_editdir.run_capt(['update-index', '-z', '--index-info'], input=input)

        tree_hash = self.git.run_capt(['write-tree'])

        if (tree_hash == self.editlog_tree and current_head == self.last_head):
            print(f'{self.repo_path}: no changes')
            return

        ctime = time.time()
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ctime))

        commit_message = f'editlog auto commit @{timestamp}'

        changed_files = []
        if self.editlog_tree:
            changed_files = self.git.run_capt(['diff', '-z', '--name-only', self.editlog_tree, tree_hash]).split('\0')
            while changed_files and not changed_files[-1]:
                changed_files.pop()

        commit_subject = []
        commit_body = []

        if current_head != self.last_head:
            commit_subject.append(f'head -> {current_head[:10]}')

        if len(changed_files) > 1:
            commit_subject.append(f'edit {changed_files[0]} [+{len(changed_files) - 1}]')
            for fn in changed_files[1:10]:
                commit_body.append(f'   + {fn}')
            if len(changed_files) >= 11:
                commit_body.append('   + ...')
        elif len(changed_files) == 1:
            commit_subject.append(f'edit {changed_files[0]}')

        commit_subject = ", ".join(commit_subject) + f' @{timestamp}'
        print(f'{self.repo_path}: changes detected, new tree = {tree_hash}, making commit: {commit_subject}')

        if commit_body:
            commit_message = [commit_subject, ''] + commit_body
        else:
            commit_message = [commit_subject]

        git_args = ['commit-tree', tree_hash, '-m', '\n'.join(commit_message)]
        if self.editlog_branch_head:
            git_args.append('-p')
            git_args.append(self.editlog_branch_head)

        if current_head != self.last_head or not self.editlog_branch_head:
            git_args.append('-p')
            git_args.append(current_head)

        new_editlog_head = self.git.run_capt(git_args)

        print(f'{self.repo_path}: created commit {new_editlog_head}')
        self.git.run(['branch', '-f', EDITLOG_BRANCH, new_editlog_head])
        if self.last_head != current_head:
            self.git.run(['branch', '-f', EDITLOG_BASE_BRANCH, current_head])

        self.editlog_branch_head = new_editlog_head
        self.editlog_tree = tree_hash
        self.last_head = current_head

def get_branch(git, branch_name):
    try:
        return git.run_capt(['rev-parse', '--verify', f'refs/heads/{branch_name}'], print_error=False)
    except subprocess.CalledProcessError:
        return None
