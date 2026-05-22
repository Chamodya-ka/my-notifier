import subprocess

from config import load_config
from matcher import Matcher


class Runner:
    def __init__(self, cmd: list[str]):
        self.cmd = cmd
        self.matcher = Matcher(load_config())

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

        for line in process.stdout:
            print(line, end="")
            self.on_line(line.rstrip("\n"))

        process.wait()
        return process.returncode
