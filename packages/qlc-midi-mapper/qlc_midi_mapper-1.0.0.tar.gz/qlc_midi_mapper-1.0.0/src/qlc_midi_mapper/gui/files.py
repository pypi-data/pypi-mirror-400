#!/usr/bin/env python3
"""File dialogs, export/import, and drag & drop for the GUI.

This mixin is responsible for all disk interactions:

- Opening a QLC+ Workspace (``.qxw``)
- Saving the modified workspace back to disk
- Importing a mapping CSV
- Exporting mapping files (CSV / Studio One pitch list / Reaper note names)
- Handling drag & drop (when ``tkinterdnd2`` is available)
"""


import os
from typing import Any

from qlc_midi_mapper.gui.base import DND_AVAILABLE, filedialog, messagebox
from qlc_midi_mapper.workspace import MidiWorkspace


class FileOperationsMixin:
    """Mixin handling open/save/export/import and drag & drop."""

    workspace: MidiWorkspace

    def open_workspace(self) -> None:
        """Open a QLC+ workspace file using a file dialog."""
        path = filedialog.askopenfilename(
            filetypes=[("QLC+ Workspace", "*.qxw"), ("All files", "*.*")],
        )
        if not path:
            return
        self._load_workspace(path)

    def _load_workspace(self, path: str) -> None:
        """Load and parse a QLC+ workspace file."""
        try:
            self.workspace.load(path)
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to parse XML file:\n{exc}")
            return

        self.status_var.set(f"Loaded: {os.path.basename(path)}")
        self.dirty = False
        self.selected_widget_index = None
        self.highlight_cc_col = None

        self.sort_mode = "index"
        self.sort_reverse = False

        self.rebuild_trees()

    def save_workspace_as(self) -> None:
        """Save the current workspace with updated MIDI mappings."""
        if not self.workspace.is_loaded:
            messagebox.showwarning("No workspace", "Load a QLC+ workspace first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".qxw",
            filetypes=[("QLC+ Workspace", "*.qxw"), ("All files", "*.*")],
        )
        if not path:
            return

        stem, _ = os.path.splitext(path)
        if self.export_csv.get():
            self.workspace.export_mapping_csv(stem + ".csv")
        if self.export_reaper.get():
            self.workspace.export_reaper(stem + ".txt")
        if self.export_studio_one.get():
            self.workspace.export_studio_one(stem + ".pitchlist")

        try:
            self.workspace.save(path)
            self.status_var.set(f"Saved workspace: {os.path.basename(path)}")
            self.dirty = False
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save workspace:\n{exc}")

    def import_mapping_csv(self) -> None:
        """Import a mapping CSV using a file dialog."""
        if not self.rows:
            messagebox.showwarning(
                "No workspace",
                "Load a QLC+ workspace before importing a mapping CSV.",
            )
            return

        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return

        self._import_mapping_csv_from_path(path)

    def _import_mapping_csv_from_path(self, path: str) -> None:
        """Import a mapping CSV from disk and refresh the view."""
        if not self.rows:
            messagebox.showwarning(
                "No workspace",
                "Load a QLC+ workspace before importing a mapping CSV.",
            )
            return

        try:
            applied_rows, unknown_names = self.workspace.import_mapping_csv(path)
            if applied_rows:
                self.dirty = True
            self.rebuild_trees()

            msg = f"Imported mapping for {applied_rows} name(s)."
            if unknown_names:
                msg += f"\n{len(unknown_names)} name(s) not found in workspace."
            self.status_var.set(msg)
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to import CSV:\n{exc}")

    def _on_drop_files(self, event: Any) -> None:
        """Handle drag & drop of files on the main window."""
        if not DND_AVAILABLE:
            return

        data = getattr(event, "data", "")
        paths = self._parse_dnd_files(str(data))
        if not paths:
            return

        for path in paths:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".qxw":
                self._load_workspace(path)
            elif ext == ".csv":
                self._import_mapping_csv_from_path(path)

    @staticmethod
    def _parse_dnd_files(data: str) -> list[str]:
        """Parse drag & drop event data into a list of paths."""
        if not data:
            return []

        files: list[str] = []
        current = ""
        in_brace = False

        for ch in data:
            if ch == "{":
                in_brace = True
                if current.strip():
                    files.append(current.strip())
                    current = ""
            elif ch == "}":
                in_brace = False
                if current:
                    files.append(current.strip())
                    current = ""
            elif ch == " " and not in_brace:
                if current:
                    files.append(current.strip())
                    current = ""
            else:
                current += ch

        if current.strip():
            files.append(current.strip())

        return files
