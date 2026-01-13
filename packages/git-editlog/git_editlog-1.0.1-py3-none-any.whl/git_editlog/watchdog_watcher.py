import sys
import re
import time
import os
import argparse
import subprocess
import logging
import traceback
import copy
from pathlib import Path

from ktpanda import git_helper
from watchdog import events, observers

from . import repo_watcher

log = logging.getLogger(__name__)

EVENTS = [
    events.FileCreatedEvent, events.DirCreatedEvent,
    events.FileDeletedEvent, events.DirDeletedEvent,
    events.FileMovedEvent, events.DirMovedEvent,
    events.FileModifiedEvent, events.DirModifiedEvent,
]

class RepoWatcher(repo_watcher.BaseRepoWatcher, events.FileSystemEventHandler):
    def on_any_event(self, event):
        path = Path(event.src_path)
        if self.path_modified(path):
            log.debug(f'{self.repo_path}: {event}')

    def setup_observer(self, observer):
        observer.schedule(self, self.repo_path, recursive=True, event_filter=EVENTS)
        if not self.git_dir.is_relative_to(self.repo_path):
            observer.schedule(self, self.git_dir, recursive=False, event_filter=EVENTS)

    @staticmethod
    def run(repo_watchers):
        observer = observers.Observer()
        for watcher in repo_watchers:
            watcher.setup_observer(observer)

        observer.start()

        next_check_time = 0

        while True:
            ctime = time.time()
            remain = next_check_time - ctime
            if remain > 0:
                time.sleep(min(5, remain))

            ctime = time.time()
            next_check_time = ctime + 1


            for watcher in repo_watchers:
                try:
                    watcher.check()
                except Exception:
                    log.exception(f'ERROR checking {watcher.repo_path}')
