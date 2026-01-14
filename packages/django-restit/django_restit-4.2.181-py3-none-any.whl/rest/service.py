import os
import signal
import time
import argparse
import logging
import daemon
from daemon import pidfile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Service(FileSystemEventHandler):
    def __init__(self, name, pid_file, watch_file=None, require_user=None, logger=None):
        self.name = name
        self.pid_file = pid_file
        self.watch_file = os.path.realpath(watch_file) if watch_file else None
        self.require_user = require_user
        self.observer = None

    def log_info(self, *args):
        if self.logger:
            self.log_info(*args)

    def start(self):
        if self.is_running():
            self.log_info("Service is already running.")
            return

        self.log_info(f"Starting {self.name}...")

        with daemon.DaemonContext(
            pidfile=pidfile.TimeoutPIDLockFile(self.pid_file),
            stdout=open('/tmp/service.log', 'a+'),
            stderr=open('/tmp/service_error.log', 'a+'),
            signal_map={
                signal.SIGTERM: self.stop,
                signal.SIGHUP: self.restart
            }
        ):
            self.run()

    def stop(self, *args):
        pid = self.get_pid()
        if not pid:
            self.log_info("Service is not running.")
            return

        self.log_info(f"Stopping {self.name} (PID: {pid})...")
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            if self.is_running():
                os.kill(pid, signal.SIGKILL)
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            self.log_info("Service stopped.")
        except OSError:
            self.logger.error(f"Failed to stop process {pid}")

    def restart(self, *args):
        self.log_info("Restarting service...")
        self.stop()
        time.sleep(1)
        self.start()

    def status(self):
        if self.is_running():
            print(f"{self.name} is running (PID: {self.get_pid()})")
        else:
            print(f"{self.name} is not running")

    def is_running(self):
        """Check if the process is running using os.kill(pid, 0)"""
        pid = self.get_pid()
        if pid:
            try:
                os.kill(pid, 0)  # Does not kill, just checks if process exists
                return True
            except OSError:
                return False
        return False

    def get_pid(self):
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, "r") as f:
                    pid = int(f.read().strip())
                return pid
            except ValueError:
                return None
        return None

    def run(self):
        """Main daemon loop"""
        self.log_info(f"{self.name} is running in background.")
        if self.watch_file:
            self.start_watcher()
        self.on_run()

    def on_run(self):
        while True:
            time.sleep(5)

    def start_watcher(self):
        self.log_info(f"Watching file: {self.watch_file}")
        self.observer = Observer()
        self.observer.schedule(self, path=os.path.dirname(self.watch_file), recursive=False)
        self.observer.start()

    def on_modified(self, event):
        if self.watch_file and event.src_path == self.watch_file:
            self.log_info("Config file changed, restarting service...")
            self.restart()


def main():
    parser = argparse.ArgumentParser(description="Manage the service daemon")
    parser.add_argument("command", choices=["start", "stop", "restart", "status", "run"])
    args = parser.parse_args()

    service = Service(name="MyDaemon", pid_file="/tmp/mydaemon.pid")

    if args.command == "start":
        service.start()
    elif args.command == "stop":
        service.stop()
    elif args.command == "restart":
        service.restart()
    elif args.command == "status":
        service.status()
    elif args.command == "run":
        service.run()

if __name__ == "__main__":
    main()
