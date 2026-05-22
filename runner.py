import os
import subprocess

from config import load_config
from matcher import Matcher


class Runner:
    def __init__(self, cmd: list[str], cwd: str | None = None):
        self.cmd = cmd
        self.cwd = cwd or os.getcwd()
        config_path = os.path.join(self.cwd, "my_notifier.yaml")
        self.matcher = Matcher(load_config(config_path))

    def on_line(self, line: str):
        self.matcher.match_line(line)

    def run(self):
        process = subprocess.Popen(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        try:
            for line in process.stdout:
                print(line, end="")
                self.on_line(line.rstrip("\n"))
        except KeyboardInterrupt:
            # Child already received SIGINT (same process group); wait briefly
            # for it to exit, then fall through to cleanup.
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait()
        finally:
            self.matcher.stop()

        process.wait()
        return process.returncode
