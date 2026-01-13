#!/usr/bin/env python3
"""Menu bar and quit handling for the MIDI matrix GUI.

This module provides a small mixin used by the main Tkinter application to:

- Create the menu bar (File menu).
- Prompt the user on quit if there are unsaved changes.

The mixin expects the hosting class to provide GUI callbacks such as
``open_workspace`` and ``save_workspace_as``.
"""


from qlc_midi_mapper.gui.base import messagebox, tk


class MenuMixin:
    """Mixin providing menu creation and quit handling."""

    def _create_menu(self) -> None:
        """Create and attach the application menu bar."""
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(
            label="Open QLC Workspace...",
            command=self.open_workspace,
        )
        file_menu.add_command(
            label="Import Mapping CSV...",
            command=self.import_mapping_csv,
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Save Workspace As...",
            command=self.save_workspace_as,
        )
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.on_quit)
        menubar.add_cascade(label="File", menu=file_menu)

        self.config(menu=menubar)

    def on_quit(self) -> None:
        """Handle application quit, prompting if there are unsaved changes."""
        if getattr(self, "dirty", False) and not messagebox.askyesno(
            "Unsaved changes",
            "There are unsaved changes. Quit anyway?",
        ):
            return
        self.destroy()
