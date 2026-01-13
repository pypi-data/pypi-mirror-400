VERSION = "1.0.1"

import sys

if sys.platform == 'linux':
    from .pyinotify_watcher import RepoWatcher
else:
    from .watchdog_watcher import RepoWatcher
