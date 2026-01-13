from __future__ import annotations

import shlex
import shutil
from contextlib import contextmanager


class SimpleConsole:
    def __init__(self):
        self.is_tty = False
        self.use_unicode = False

    def icon(self, kind: str) -> str:
        return {
            "info": "i",
            "ok": "+",
            "warn": "!",
            "err": "x",
            "run": ">",
            "spark": "*",
        }.get(kind, "*")

    def rule(self, title: str = "") -> None:
        width = 80
        try:
            width = shutil.get_terminal_size((80, 20)).columns
        except Exception:
            pass
        line = "-" * max(1, width)
        if title:
            print(line)
            print(title)
        print(line)

    def info(self, msg: str) -> None:
        print(f"{self.icon('info')} {msg}")

    def success(self, msg: str) -> None:
        print(f"{self.icon('ok')} {msg}")

    def warn(self, msg: str) -> None:
        print(f"{self.icon('warn')} {msg}")

    def error(self, msg: str) -> None:
        print(f"{self.icon('err')} {msg}")

    def cmd(self, argv: list[str], label: str = "run") -> None:
        try:
            joined = shlex.join(argv)
        except Exception:
            joined = " ".join(argv)
        print(f"{self.icon('run')} {label}: {joined}")

    @contextmanager
    def spinner(self, text: str, detail: str | None = None):
        print(f"{self.icon('spark')} {text}" + (f" — {detail}" if detail else ""))
        try:
            yield
        except Exception as e:
            self.error(f"{text} failed: {e}")
            raise
        else:
            self.success(f"{text} done")


# TODO
# class AnsiConsole()

console = SimpleConsole()
