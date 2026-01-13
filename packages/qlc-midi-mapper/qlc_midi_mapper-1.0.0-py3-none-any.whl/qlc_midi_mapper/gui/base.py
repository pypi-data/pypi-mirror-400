#!/usr/bin/env python3
"""Shared Tkinter imports and optional drag & drop support.

The GUI package centralizes Tkinter imports here so other modules can simply do::

    from .base import tk, ttk, messagebox

The module also provides optional drag & drop support via ``tkinterdnd2``.
If the dependency is not available, the application falls back to standard
file dialogs.
"""


import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

# Optional drag & drop support via tkinterdnd2.
try:  # pragma: no cover - optional dependency
    from tkinterdnd2 import DND_FILES, TkinterDnD

    BaseTk = TkinterDnD.Tk
    DND_AVAILABLE = True
except Exception:  # pragma: no cover
    BaseTk = tk.Tk
    DND_AVAILABLE = False
    DND_FILES = None

__all__ = [
    "DND_AVAILABLE",
    "DND_FILES",
    "BaseTk",
    "filedialog",
    "messagebox",
    "tk",
    "tkfont",
    "ttk",
]
