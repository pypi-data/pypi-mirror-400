import math
import re
import sys
import time
from dataclasses import dataclass, field
from shutil import get_terminal_size
from typing import Iterable, Iterator, Optional, TextIO, TypeVar


_COLOR = {
    "RESET": "\x1b[0m",
    "RED": "\x1b[31m",
    "GREEN": "\x1b[32m",
    "YELLOW": "\x1b[33m",
    "BLUE": "\x1b[34m",
    "MAGENTA": "\x1b[35m",
    "CYAN": "\x1b[36m",
    "WHITE": "\x1b[37m",
}

_STYLES = {
    "dash": {"fill": "-", "empty": " ", "left": "[", "right": "]"},
    "block": {"fill": "=", "empty": ".", "left": "[", "right": "]"},
    "pipe": {"fill": "|", "empty": " ", "left": "|", "right": "|"},
    "dot": {"fill": ".", "empty": " ", "left": "(", "right": ")"},
    "chevron": {"fill": ">", "empty": " ", "left": "<", "right": ">"},
    "packages": {"fill": "-", "empty": " ", "left": "", "right": ""},
}

_SPINNER_FRAMES = ["⠴", "⠸", "⠹", "⠺", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

T = TypeVar("T")


def _visible_len(text: str) -> int:
    return len(_ANSI_RE.sub("", text))


def _screen_lines(lines: list[str], term_width: int) -> int:
    width = max(1, term_width)
    total = 0
    for line in lines:
        vis = _visible_len(line)
        total += max(1, math.ceil(vis / width))
    return total

@dataclass
class ProgressBar:
    description: str = ""
    total_size: float = 100.0
    item: str = ""
    width: int = 30
    fill_char: str = "-"
    empty_char: str = "-"
    left_bracket: str = "["
    right_bracket: str = "]"
    style: Optional[str] = None
    unit: str = ""
    label_width: int = 16
    spinner_frames: Optional[list] = None
    color: Optional[str] = "blue"
    auto_done: bool = True
    managed: bool = False
    manager: Optional[object] = None
    stream: Optional[TextIO] = None
    current: float = 0.0
    start_time: float = field(default_factory=time.time)
    _last_render_len: int = 0
    _rendered_lines: int = 0
    _spinner_index: int = 0
    _done: bool = False

    def update(self, advance: Optional[float] = None, *, current: Optional[float] = None, item: Optional[str] = None) -> None:
        if self._done:
            return
        if current is not None:
            self.current = float(current)
        elif advance is not None:
            self.current += float(advance)

        if item is not None:
            self.item = item

        if self.auto_done and self.total_size > 0 and self.current >= self.total_size:
            self.done()
            return
        if self.managed and self.manager:
            self.manager.render()
            return
        self._render()

    def done(self) -> None:
        if self._done:
            return
        self._done = True
        self.current = self.total_size
        if self.managed:
            if self.manager:
                self.manager.render()
            return
        self._render(final=True)
        if self.style != "packages":
            stream = self.stream or sys.stdout
            stream.write("\n")
            stream.flush()

    def iter(self, iterable: Iterable[T]) -> Iterator[T]:
        for value in iterable:
            yield value
            self.update(1)
        if not self._done:
            self.done()

    def _render(self, final: bool = False) -> None:
        lines = self.render_lines()
        if self.style == "packages":
            self._write_lines(lines, final=final)
            return

        line = lines[0] if lines else ""
        pad = max(0, self._last_render_len - len(line))
        self._last_render_len = len(line)
        end = "" if final else ""
        stream = self.stream or sys.stdout
        stream.write("\r" + line + (" " * pad) + end)
        stream.flush()

    def render_lines(self, *, single_line: bool = False) -> list:
        self._apply_style()
        if self.total_size <= 0:
            ratio = 1.0
        else:
            ratio = min(max(self.current / self.total_size, 0.0), 1.0)

        term_width = get_terminal_size((80, 20)).columns
        percent = int(ratio * 100)

        desc_text = self.description or ""
        item_text = self.item or ""
        count = f"{self._format_num(self.current)}{self.unit}/{self._format_num(self.total_size)}{self.unit}"
        if self.style == "packages":
            bar_width = self._packages_bar_width(term_width, count)
            filled = int(bar_width * ratio)
            empty = bar_width - filled
            bar = self._render_bar(filled, empty)
            if single_line:
                return [self._render_packages_single_line(desc_text.strip(), count, bar)]
            return self._render_packages(desc.strip(), count, bar, term_width)

        bar_width = self._standard_bar_width(term_width, count)
        filled = int(bar_width * ratio)
        empty = bar_width - filled
        bar = self._render_bar(filled, empty)

        desc, item = self._fit_text(term_width, bar_width, count, desc_text, item_text)
        line = f"{desc}{self.left_bracket}{bar}{self.right_bracket} {percent:3d}% {count}{item}"
        return [line]

    @staticmethod
    def _format_num(value: float) -> str:
        if isinstance(value, int):
            return str(value)
        if value.is_integer():
            return str(int(value))
        return f"{value:.2f}"

    def _apply_color(self, text: str) -> str:
        stream = self.stream or sys.stdout
        if not self.color or not stream.isatty():
            return text
        code = _COLOR.get(self.color.upper())
        if not code:
            return text
        return f"{code}{text}{_COLOR['RESET']}"

    def _render_bar(self, filled: int, empty: int) -> str:
        filled_text = self.fill_char * filled
        empty_text = self.empty_char * empty
        return f"{self._apply_color(filled_text)}{empty_text}"

    def _apply_style(self) -> None:
        if not self.style:
            return
        style = _STYLES.get(self.style)
        if not style:
            return
        self.fill_char = style["fill"]
        self.empty_char = style["empty"]
        self.left_bracket = style["left"]
        self.right_bracket = style["right"]

    def _render_packages(self, desc: str, count: str, bar: str, term_width: int) -> list:
        spinner = self._next_spinner()
        total = int(self.total_size) if float(self.total_size).is_integer() else self.total_size
        current = int(self.current) if float(self.current).is_integer() else self.current
        base1 = f"{spinner}  ({current}/{total})"
        available = max(0, term_width - len(base1) - 1)
        trimmed_desc = desc[:available]
        line1 = f"{spinner} {trimmed_desc} ({current}/{total})".rstrip()
        label = (self.item or "").ljust(self.label_width)[: self.label_width]
        line2 = f"{label} {bar} {count}".rstrip()
        return [line1, line2]

    def _render_packages_single_line(self, desc: str, count: str, bar: str) -> str:
        spinner = self._next_spinner()
        total = int(self.total_size) if float(self.total_size).is_integer() else self.total_size
        current = int(self.current) if float(self.current).is_integer() else self.current
        label = (self.item or "").strip()
        parts = [f"{spinner} {desc} ({current}/{total})"]
        if label:
            parts.append(label)
        parts.append(bar)
        parts.append(count)
        return " ".join(part for part in parts if part)

    def _standard_bar_width(self, term_width: int, count: str) -> int:
        fixed = len(self.left_bracket) + len(self.right_bracket)
        fixed += 1 + 4 + 1 + len(count)
        return min(self.width, max(1, term_width - fixed - 2))

    def _packages_bar_width(self, term_width: int, count: str) -> int:
        fixed = self.label_width + 1 + len(count)
        return min(self.width, max(1, term_width - fixed - 1))

    def _fit_text(
        self,
        term_width: int,
        bar_width: int,
        count: str,
        desc_text: str,
        item_text: str,
    ) -> tuple:
        fixed = len(self.left_bracket) + len(self.right_bracket)
        fixed += bar_width + 1 + 4 + 1 + len(count)
        available = max(0, term_width - fixed)
        desc = ""
        item = ""
        if desc_text and available > 0:
            keep = min(len(desc_text), available)
            desc = desc_text[:keep]
            if desc:
                desc += " "
        available -= len(desc)
        if item_text and available > 0:
            keep = min(len(item_text), max(0, available - 1))
            if keep > 0:
                item = " " + item_text[:keep]
        return desc, item

    def _write_lines(self, lines: list, final: bool = False) -> None:
        stream = self.stream or sys.stdout
        if stream.isatty() and self._rendered_lines:
            stream.write(f"\x1b[{self._rendered_lines}A")
        for idx, line in enumerate(lines):
            if stream.isatty():
                stream.write("\r\x1b[2K")
            stream.write(line)
            if idx < len(lines) - 1:
                stream.write("\n")
        if final:
            stream.write("\n")
            self._rendered_lines = 0
        else:
            self._rendered_lines = len(lines)
        stream.flush()

    def _next_spinner(self) -> str:
        frames = self.spinner_frames or _SPINNER_FRAMES
        frame = frames[self._spinner_index % len(frames)]
        self._spinner_index += 1
        return frame


class MultiProgress:
    def __init__(self, stream: Optional[TextIO] = None, *, force_tty: bool = False) -> None:
        self.stream = stream or sys.stdout
        self.force_tty = force_tty
        self._bars: list[ProgressBar] = []
        self._rendered_lines: int = 0

    def add(self, bar: ProgressBar) -> ProgressBar:
        bar.managed = True
        bar.manager = self
        bar.stream = self.stream
        self._bars.append(bar)
        return bar

    def render(self, final: bool = False) -> None:
        if not self._bars:
            return
        lines: list[str] = []
        for bar in self._bars:
            lines.extend(bar.render_lines())
        prev_lines = self._rendered_lines
        if self._isatty() and prev_lines:
            if prev_lines > 1:
                self.stream.write(f"\x1b[{prev_lines - 1}A")
            self.stream.write("\r")
        for idx, line in enumerate(lines):
            if self._isatty():
                self.stream.write("\r\x1b[2K")
            self.stream.write(line)
            if idx < len(lines) - 1:
                self.stream.write("\n")
        term_width = get_terminal_size((80, 20)).columns
        rendered = _screen_lines(lines, term_width)
        if self._isatty() and prev_lines > rendered:
            extra = prev_lines - rendered
            for _ in range(extra):
                self.stream.write("\n\r\x1b[2K")
            self.stream.write(f"\x1b[{extra}A")
        if final:
            self.stream.write("\n")
            self._rendered_lines = 0
        else:
            self._rendered_lines = rendered
        self.stream.flush()

    def write_line(self, text: str) -> None:
        if self._isatty() and self._rendered_lines:
            if self._rendered_lines > 1:
                self.stream.write(f"\x1b[{self._rendered_lines - 1}A")
            self.stream.write("\r")
            for idx in range(self._rendered_lines):
                self.stream.write("\r\x1b[2K")
                if idx < self._rendered_lines - 1:
                    self.stream.write("\n")
        self.stream.write(text + "\n")
        self._rendered_lines = 0
        self.render()

    def done(self) -> None:
        for bar in self._bars:
            bar.done()
        self.render(final=True)

    def _isatty(self) -> bool:
        return self.force_tty or self.stream.isatty()


class SingleProgress:
    def __init__(
        self,
        stream: Optional[TextIO] = None,
        *,
        force_tty: bool = False,
        keep_finished: bool = True,
        single_line_only: bool = False,
    ) -> None:
        self.stream = stream or sys.stdout
        self.force_tty = force_tty
        self.keep_finished = keep_finished
        self.single_line_only = single_line_only
        self._bar: Optional[ProgressBar] = None
        self._rendered_lines: int = 0

    def add(self, bar: ProgressBar) -> ProgressBar:
        if self._bar and not self._bar._done:
            self._finalize()
        elif self._bar and self._bar._done and not self.keep_finished:
            self._clear_rendered()
        bar.managed = True
        bar.manager = self
        bar.stream = self.stream
        self._bar = bar
        return bar

    def render(self) -> None:
        if not self._bar:
            return
        if self._bar._done:
            if self.keep_finished:
                self._finalize()
            else:
                self._clear_rendered()
                self._bar = None
            return
        self._render_lines(self._bar.render_lines(single_line=self.single_line_only))

    def write_line(self, text: str) -> None:
        if self._isatty() and self._rendered_lines:
            if self._rendered_lines > 1:
                self.stream.write(f"\x1b[{self._rendered_lines - 1}A")
            self.stream.write("\r")
            for idx in range(self._rendered_lines):
                self.stream.write("\r\x1b[2K")
                if idx < self._rendered_lines - 1:
                    self.stream.write("\n")
        self.stream.write(text + "\n")
        self._rendered_lines = 0
        if self._bar and not self._bar._done:
            self.render()

    def done(self) -> None:
        if self._bar and not self._bar._done:
            self._bar.done()
        self._finalize()

    def _render_lines(self, lines: list[str], *, final: bool = False) -> None:
        if self._isatty() and self._rendered_lines:
            if self._rendered_lines > 1:
                self.stream.write(f"\x1b[{self._rendered_lines - 1}A")
            self.stream.write("\r")
        for idx, line in enumerate(lines):
            if self._isatty():
                self.stream.write("\r\x1b[2K")
            self.stream.write(line)
            if idx < len(lines) - 1:
                self.stream.write("\n")
        term_width = get_terminal_size((80, 20)).columns
        rendered = _screen_lines(lines, term_width)
        if final:
            self.stream.write("\n")
            self._rendered_lines = 0
        else:
            self._rendered_lines = rendered
        self.stream.flush()

    def _finalize(self) -> None:
        if not self._bar:
            return
        lines = self._bar.render_lines(single_line=self.single_line_only)
        if self.keep_finished:
            self._render_lines(lines, final=True)
        else:
            self._clear_rendered()
        self._bar = None

    def _clear_rendered(self) -> None:
        if not (self._isatty() and self._rendered_lines):
            self._rendered_lines = 0
            return
        if self._rendered_lines > 1:
            self.stream.write(f"\x1b[{self._rendered_lines - 1}A")
        self.stream.write("\r")
        for idx in range(self._rendered_lines):
            self.stream.write("\r\x1b[2K")
            if idx < self._rendered_lines - 1:
                self.stream.write("\n")
        self._rendered_lines = 0
        self.stream.flush()

    def _isatty(self) -> bool:
        return self.force_tty or self.stream.isatty()
