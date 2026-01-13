#!/usr/bin/env python3
"""Main Tkinter application for the MIDI routing matrix GUI."""


from qlc_midi_mapper.gui.base import DND_AVAILABLE, DND_FILES, BaseTk, tk
from qlc_midi_mapper.gui.events import EventsMixin
from qlc_midi_mapper.gui.files import FileOperationsMixin
from qlc_midi_mapper.gui.layout import LayoutMixin
from qlc_midi_mapper.gui.menu import MenuMixin
from qlc_midi_mapper.models import RowEntry
from qlc_midi_mapper.workspace import MidiWorkspace


class MidiMatrixApp(BaseTk, MenuMixin, LayoutMixin, FileOperationsMixin, EventsMixin):
    """Main application window.

    The application is built as a composition of mixins to keep responsibilities
    separated (menu, layout, file operations, and interactive events).
    """

    def __init__(self) -> None:
        """Initialize the main window and build the UI."""
        BaseTk.__init__(self)

        self.title("QLC+ MIDI Routing Matrix")
        self.geometry("1600x900")

        # Backend workspace
        self.workspace = MidiWorkspace()

        # View-related state
        self.sort_mode: str = "index"  # "index", "name", "func", "midi", "path"
        self.sort_reverse: bool = False
        self.dirty: bool = False

        # Frozen + matrix columns
        self.fixed_columns: list[str] = ["index", "caption", "func", "path", "midi"]
        self.cc_columns: list[str] = []

        # Matrix width (number of MIDI numbers shown per row)
        self.matrix_width_var = tk.IntVar(value=128)

        self.status_var = tk.StringVar(value="No file loaded")

        self.selected_widget_index: int | None = None
        self.highlight_cc_col: str | None = None

        self.widget_to_row_index: dict[int, int] = {}

        self.info_tree = None
        self.matrix_tree = None
        self.v_scrollbar = None

        self._syncing_selection: bool = False
        self._is_building: bool = False

        # Build UI
        self._create_menu()
        self._create_main_layout()

        # Drag & drop on root
        if DND_AVAILABLE:
            try:
                self.drop_target_register(DND_FILES)
                self.dnd_bind("<<Drop>>", self._on_drop_files)
                self.status_var.set(
                    "Drag & drop enabled - drop .qxw or .csv files.",
                )
            except Exception:
                self.status_var.set(
                    "Drag & drop failed to initialize - using normal file dialogs.",
                )
        else:
            self.status_var.set(
                "Drag & drop unavailable (install 'tkinterdnd2' to enable it).",
            )

    @property
    def rows(self) -> list[RowEntry]:
        """Expose workspace rows to mixins as a convenience property."""
        return self.workspace.rows

    @rows.setter
    def rows(self, value: list[RowEntry]) -> None:
        """Set workspace rows (mainly for type-checkers and tests)."""
        self.workspace.rows = value
