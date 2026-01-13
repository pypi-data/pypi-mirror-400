import sys
import time
from dataclasses import dataclass, field
from typing import Optional, Protocol, TextIO


_COLOR = {
    "INFO": "\x1b[36m",
    "WARN": "\x1b[33m",
    "ERROR": "\x1b[31m",
    "RESET": "\x1b[0m",
}


def _supports_color() -> bool:
    return sys.stdout.isatty()


class _ProgressWriter(Protocol):
    def write_line(self, text: str) -> None:
        ...


@dataclass
class Logger:
    use_color: bool = _supports_color()
    stream: TextIO = field(default_factory=lambda: sys.stdout)
    progress: Optional[_ProgressWriter] = None

    def log(self, level: str, message: str) -> None:
        ts = time.strftime("%H:%M:%S")
        prefix = f"[{level}]"
        if self.use_color and level in _COLOR:
            colored = f"{_COLOR[level]}{prefix}{_COLOR['RESET']}"
        else:
            colored = prefix
        line = f"{ts} {colored} {message}"
        if self.progress:
            self.progress.write_line(line)
        else:
            self.stream.write(f"{line}\n")
            self.stream.flush()

    def info(self, message: str) -> None:
        self.log("INFO", message)

    def warn(self, message: str) -> None:
        self.log("WARN", message)

    def error(self, message: str) -> None:
        self.log("ERROR", message)
