import sys
import re
import time
import os
import argparse
import subprocess
import traceback
import select
import logging

from pathlib import Path

from . import repo_watcher
from . import pyinotify
from .pyinotify import WatchManager, Notifier, ProcessEvent

log = logging.getLogger(__name__)

EVENTS = (
    pyinotify.IN_CLOSE_WRITE | pyinotify.IN_CREATE |
    pyinotify.IN_DELETE | pyinotify.IN_DELETE_SELF |
    pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO |
    pyinotify.IN_MOVE_SELF
)

class Processor(ProcessEvent):
    def my_init(self, repo_watcher):
        self.watcher = repo_watcher


class RepoWatcher(repo_watcher.BaseRepoWatcher):
    def process_event(self, event):
        path = Path(event.pathname)
        triggered = self.path_modified(path)
        if triggered:

            try:
                relpath = path.relative_to(self.repo_path)
                log.debug(f'{self.repo_path}: [{event.maskname}] {relpath}')
            except ValueError:
                log.debug(f'{self.repo_path}: [{event.maskname}] {path}')

    def exclude_filter(self, path):
        path = Path(path)

        cpath = path
        while cpath != self.repo_path:
            if cpath == self.git_dir:
                return True

            if cpath.name == '.git':
                return True

            nextpath = cpath.parent
            if nextpath == cpath:
                break
            cpath = nextpath

        return False

    def setup_watch(self, wm):
        wm.add_watch(
            str(self.repo_path),
            EVENTS,
            rec = True,
            auto_add = True,
            proc_fun = self.process_event,
            exclude_filter = self.exclude_filter
        )

        wm.add_watch(
            str(self.git_dir),
            EVENTS,
            rec = False,
            auto_add = False,
            proc_fun = self.process_event
        )

        wm.add_watch(
            str(self.git_dir / 'refs'),
            EVENTS,
            rec = True,
            auto_add = True,
            proc_fun = self.process_event
        )

        wm.add_watch(
            str(self.git_dir / 'info'),
            EVENTS,
            rec = True,
            auto_add = True,
            proc_fun = self.process_event
        )

    @staticmethod
    def run(repo_watchers):
        wm = WatchManager()
        fd = wm.get_fd()

        for watcher in repo_watchers:
            watcher.setup_watch(wm)

        notifier = Notifier(wm)

        next_check_time = 0

        while True:
            ctime = time.time()
            remain = next_check_time - ctime

            ms_sleep = int(max(0, min(5, remain)) * 1000)
            if notifier.check_events(ms_sleep):
                notifier.read_events()
            notifier.process_events()

            if remain <= 0:

                ctime = time.time()
                next_check_time += 1.0
                if next_check_time < ctime:
                    next_check_time = ctime + 1

                for watcher in repo_watchers:
                    try:
                        watcher.check()
                    except Exception:
                        log.exception(f'ERROR checking {watcher.repo_path}')
