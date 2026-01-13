from __future__ import annotations

import msvcrt


def read_masked(prompt: str) -> str:
    """
    Windows CMD-safe masked input that supports:
      - typing (echoes '*' for characters)
      - backspace
      - Ctrl+V paste (reads from clipboard)
      - Enter to submit
    """
    print(prompt, end="", flush=True)

    buf: list[str] = []

    while True:
        ch = msvcrt.getwch()

        if ch in ("\r", "\n"):
            print()
            return "".join(buf).strip()

        if ch == "\b":
            if buf:
                buf.pop()
                print("\b \b", end="", flush=True)
            continue

        if ch == "\x03":
            raise KeyboardInterrupt

        if ch == "\x16":
            try:
                import tkinter as tk
                r = tk.Tk()
                r.withdraw()
                pasted = r.clipboard_get()
                r.destroy()
            except Exception:
                pasted = ""
            if pasted:
                buf.append(pasted)
                print("*" * len(pasted), end="", flush=True)
            continue

        if ord(ch) < 32:
            continue

        buf.append(ch)
        print("*", end="", flush=True)
