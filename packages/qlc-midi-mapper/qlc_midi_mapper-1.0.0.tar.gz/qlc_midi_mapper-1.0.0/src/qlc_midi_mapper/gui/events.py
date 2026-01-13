#!/usr/bin/env python3

"""Treeview events, sorting, scrolling, and matrix interactions.

This mixin contains most of the interactive behavior for the GUI:

- Building the two synchronized Treeviews (info + routing matrix)
- Sorting rows by various keys
- Editing cells and toggling MIDI routing in the matrix
- Keeping selection and scrolling synchronized
"""


from qlc_midi_mapper.gui.base import tk
from qlc_midi_mapper.models import RowEntry, VCWidget
from qlc_midi_mapper.workspace import decode_qlc_input_channel, encode_qlc_input_channel


class EventsMixin:
    """Mixin implementing view rebuilding, sorting and interactions."""

    rows: list[RowEntry]
    widget_to_row_index: dict[int, int]
    cc_columns: list[str]
    fixed_columns: list[str]

    def _configure_matrix_columns(self) -> None:
        """Configure matrix columns safely: only run when matrix has no rows."""
        if self.matrix_tree is None:
            return

        if len(self.matrix_tree.get_children()) != 0:
            self.after(1, self._configure_matrix_columns)
            return

        width = max(1, min(128, int(self.matrix_width_var.get())))
        self.cc_columns = [f"cc_{i}" for i in range(width)]

        self.matrix_tree["columns"] = self.cc_columns
        self.matrix_tree["displaycolumns"] = self.cc_columns

        for col in self.cc_columns:
            cc = int(col.split("_", 1)[1])
            self.matrix_tree.heading(col, text=str(cc))
            self.matrix_tree.column(col, width=30, anchor=tk.CENTER, stretch=False)

    def _setup_info_heading_sort_handlers(self) -> None:
        """Attach sorting handlers to info-tree column headers."""
        if self.info_tree is None:
            return

        for col in self.fixed_columns:
            text = self.info_tree.heading(col, "text")

            def _handler(c: str = col) -> None:
                self._on_info_heading_click(c)

            self.info_tree.heading(col, text=text, command=_handler)

    def _apply_matrix_column_highlight(self) -> None:
        """Apply visual highlight to the selected CC column header."""
        if self.matrix_tree is None:
            return

        for col in self.cc_columns:
            cc = int(col.split("_", maxsplit=1)[1])
            base_text = str(cc)

            if self.highlight_cc_col is not None and col == self.highlight_cc_col:
                header_text = f"▶ {base_text}"
            else:
                header_text = base_text

            self.matrix_tree.heading(col, text=header_text)

    # ------------------------------------------------------------------
    # Rebuild and sorting
    # ------------------------------------------------------------------

    def rebuild_trees(self) -> None:
        """Rebuild both Treeviews based on current settings."""
        if self.info_tree is None or self.matrix_tree is None:
            return

        self._is_building = True
        self.status_var.set("Rebuilding view...")

        for row in self.info_tree.get_children():
            self.info_tree.delete(row)
        for row in self.matrix_tree.get_children():
            self.matrix_tree.delete(row)
        self.widget_to_row_index.clear()

        self._configure_matrix_columns()

        if not self.rows:
            self._is_building = False
            self.status_var.set("No widgets in workspace.")
            return

        width = len(self.cc_columns)

        selected_row_index: int | None = None
        if self.selected_widget_index is not None:
            tmp_map: dict[int, int] = {}
            for r_idx, row in enumerate(self.rows):
                for w in row.group:
                    tmp_map[w.index] = r_idx
            selected_row_index = tmp_map.get(self.selected_widget_index)

        for row_index, row in enumerate(self.rows):
            w = row.primary

            # Display the *real* MIDI number (0-127) depending on widget type.
            if w.midi_channel is None:
                midi_display = ""
            else:
                _, midi_num = decode_qlc_input_channel(int(w.midi_channel), w.widget_type)
                midi_display = str(midi_num)

            kind_label = "Button" if getattr(w, "widget_type", "") == "Button" else "Fader"
            info_values = [
                row.id,
                kind_label,
                w.caption or f"[{w.widget_type}]",
                w.func_name,
                w.path,
                midi_display,
            ]

            tags = ("evenrow",) if row_index % 2 == 0 else ("oddrow",)

            info_id = self.info_tree.insert("", "end", values=info_values, tags=tags)

            matrix_values: list[str] = [""] * width
            if w.midi_channel is not None:
                _, cc = decode_qlc_input_channel(int(w.midi_channel), w.widget_type)
                if 0 <= cc < width:
                    matrix_values[cc] = "●"

            matrix_id = self.matrix_tree.insert(
                "",
                "end",
                values=matrix_values,
                tags=tags,
            )

            for gw in row.group:
                self.widget_to_row_index[gw.index] = row_index

            if selected_row_index is not None and row_index == selected_row_index:
                self.info_tree.selection_set(info_id)
                self.info_tree.focus(info_id)
                self.info_tree.see(info_id)

                self.matrix_tree.selection_set(matrix_id)
                self.matrix_tree.focus(matrix_id)
                self.matrix_tree.see(matrix_id)

        self.info_tree.tag_configure("evenrow", background="#ffffff")
        self.info_tree.tag_configure("oddrow", background="#f4f4ff")
        self.matrix_tree.tag_configure("evenrow", background="#ffffff")
        self.matrix_tree.tag_configure("oddrow", background="#f4f4ff")

        self._autosize_info_columns()

        if self.highlight_cc_col is not None and self.highlight_cc_col not in self.cc_columns:
            self.highlight_cc_col = None
        self._apply_matrix_column_highlight()

        self._is_building = False
        self.status_var.set(f"{len(self.rows)} rows loaded - {len(self.cc_columns)} MIDI columns.")

    def _on_info_heading_click(self, column: str) -> None:
        """Handle clicks on info-tree column headers to change sorting."""
        if self._is_building:
            return

        col_to_mode = {
            "index": "index",
            "caption": "name",
            "func": "func",
            "midi": "midi",
            "path": "path",
        }
        mode = col_to_mode.get(column)
        if mode is None:
            return

        if self.sort_mode == mode:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_mode = mode
            self.sort_reverse = False

        self._sort_rows()
        self.rebuild_trees()

    def _sort_rows(self) -> None:
        """Sort logical rows according to the selected sort mode."""
        if not self.rows:
            return

        if self.sort_mode == "index":
            self.rows.sort(key=lambda r: r.id)
        elif self.sort_mode == "name":
            self.rows.sort(key=lambda r: (r.primary.caption.lower(), r.primary.index))
        elif self.sort_mode == "func":
            self.rows.sort(
                key=lambda r: (
                    r.primary.func_name.lower(),
                    r.primary.caption.lower(),
                    r.primary.index,
                ),
            )
        elif self.sort_mode == "midi":
            self.rows.sort(
                key=lambda r: (
                    9999 if r.primary.midi_channel is None else r.primary.midi_channel,
                    r.primary.index,
                ),
            )
        elif self.sort_mode == "path":
            self.rows.sort(
                key=lambda r: (
                    r.primary.path.lower(),
                    r.primary.caption.lower(),
                    r.primary.index,
                ),
            )

        if self.sort_reverse:
            self.rows.reverse()

    # ------------------------------------------------------------------
    # Selection sync
    # ------------------------------------------------------------------

    def _on_info_select(self, event=None) -> None:
        """Sync selection from left Treeview to right Treeview."""
        if self._is_building or self._syncing_selection:
            return
        sel = self.info_tree.selection()
        if not sel:
            return

        row = self.info_tree.index(sel[0])
        matrix_children = self.matrix_tree.get_children()
        if row >= len(matrix_children):
            return

        matrix_id = matrix_children[row]

        self._syncing_selection = True
        try:
            if self.matrix_tree.selection() != (matrix_id,):
                self.matrix_tree.selection_set(matrix_id)
                self.matrix_tree.focus(matrix_id)
                self.matrix_tree.see(matrix_id)
        finally:
            self._syncing_selection = False

    def _on_matrix_select(self, event=None) -> None:
        """Sync selection from right Treeview to left Treeview."""
        if self._is_building or self._syncing_selection:
            return
        sel = self.matrix_tree.selection()
        if not sel:
            return

        row = self.matrix_tree.index(sel[0])
        info_children = self.info_tree.get_children()
        if row >= len(info_children):
            return

        info_id = info_children[row]

        self._syncing_selection = True
        try:
            if self.info_tree.selection() != (info_id,):
                self.info_tree.selection_set(info_id)
                self.info_tree.focus(info_id)
                self.info_tree.see(info_id)
        finally:
            self._syncing_selection = False

    # ------------------------------------------------------------------
    # Matrix click handlers
    # ------------------------------------------------------------------

    def on_matrix_click(self, event: tk.Event) -> None:
        """Handle single mouse click on the matrix Treeview."""
        if self._is_building or self.matrix_tree is None or self.info_tree is None:
            return

        region = self.matrix_tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.matrix_tree.identify_row(event.y)
        col_id = self.matrix_tree.identify_column(event.x)
        if not row_id or not col_id:
            return

        row_index = self.matrix_tree.index(row_id)
        if row_index < 0 or row_index >= len(self.rows):
            return
        row = self.rows[row_index]
        w = row.primary
        self.selected_widget_index = w.index

        matrix_children = self.matrix_tree.get_children()
        info_children = self.info_tree.get_children()
        if row_index < len(matrix_children):
            self.matrix_tree.selection_set(matrix_children[row_index])
            self.matrix_tree.focus(matrix_children[row_index])
        if row_index < len(info_children):
            self.info_tree.selection_set(info_children[row_index])
            self.info_tree.focus(info_children[row_index])

        try:
            col_index = int(col_id.replace("#", "")) - 1
        except ValueError:
            return

        display_cols = list(self.matrix_tree["displaycolumns"])
        if col_index < 0 or col_index >= len(display_cols):
            self.highlight_cc_col = None
            self._apply_matrix_column_highlight()
            return

        col_name = display_cols[col_index]

        if col_name.startswith("cc_"):
            self.highlight_cc_col = col_name
        else:
            self.highlight_cc_col = None
        self._apply_matrix_column_highlight()

    def on_matrix_double_click(self, event: tk.Event) -> None:
        """Handle double-click on the matrix Treeview to toggle routing."""
        if self._is_building or self.matrix_tree is None or self.info_tree is None:
            return

        self.on_matrix_click(event)

        region = self.matrix_tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.matrix_tree.identify_row(event.y)
        col_id = self.matrix_tree.identify_column(event.x)
        if not row_id or not col_id:
            return

        row_index = self.matrix_tree.index(row_id)
        if row_index < 0 or row_index >= len(self.rows):
            return
        row = self.rows[row_index]
        w = row.primary
        self.selected_widget_index = w.index

        try:
            col_index = int(col_id.replace("#", "")) - 1
        except ValueError:
            return

        display_cols = list(self.matrix_tree["displaycolumns"])
        if col_index < 0 or col_index >= len(display_cols):
            return

        col_name = display_cols[col_index]
        if not col_name.startswith("cc_"):
            return

        try:
            cc = int(col_name.split("_", maxsplit=1)[1])
        except ValueError:
            return

        real_channel = encode_qlc_input_channel(w.widget_type, cc, previous=w.midi_channel)

        if w.midi_channel == real_channel:
            new_channel: int | None = None
        else:
            new_channel = real_channel

        self.set_widget_channel(w, new_channel)

    def set_widget_channel(self, w: VCWidget, channel: int | None) -> None:
        """Set the MIDI channel for a VCWidget and refresh only its logical row."""
        if self.info_tree is None or self.matrix_tree is None:
            return
        if self._is_building:
            return

        row_index = self.widget_to_row_index.get(w.index)
        if row_index is None or row_index < 0 or row_index >= len(self.rows):
            self.rebuild_trees()
            return

        row = self.rows[row_index]

        old_channel = row.primary.midi_channel

        for gw in row.group:
            gw.midi_channel = channel

        self.dirty = True

        info_children = self.info_tree.get_children()
        matrix_children = self.matrix_tree.get_children()
        if row_index >= len(info_children) or row_index >= len(matrix_children):
            self.rebuild_trees()
            return

        info_id = info_children[row_index]
        matrix_id = matrix_children[row_index]

        if channel is None:
            midi_display = ""
        else:
            _, midi_num = decode_qlc_input_channel(int(channel), w.widget_type)
            midi_display = str(midi_num)
        self.info_tree.set(info_id, "midi", midi_display)

        width = len(self.cc_columns)
        values = list(self.matrix_tree.item(matrix_id, "values"))
        if len(values) < width:
            values.extend([""] * (width - len(values)))

        if old_channel is not None:
            _, old_cc = decode_qlc_input_channel(int(old_channel), w.widget_type)
            if 0 <= old_cc < width:
                values[old_cc] = ""

        if channel is not None:
            _, new_cc = decode_qlc_input_channel(int(channel), w.widget_type)
            if 0 <= new_cc < width:
                values[new_cc] = "●"
                self.highlight_cc_col = f"cc_{new_cc}"
            else:
                self.highlight_cc_col = None
        else:
            self.highlight_cc_col = None

        self.matrix_tree.item(matrix_id, values=values)
        self._apply_matrix_column_highlight()

    # ------------------------------------------------------------------
    # Mouse wheel scroll sync
    # ------------------------------------------------------------------

    def _on_mousewheel(self, event: tk.Event) -> str:
        """Scroll both trees together with the mouse wheel (Windows/macOS)."""
        if self.info_tree is None or self.matrix_tree is None:
            return "break"
        delta = 0
        if event.delta != 0:
            delta = -1 * int(event.delta / 120)
        if delta != 0:
            self.info_tree.yview_scroll(delta, "units")
            self.matrix_tree.yview_scroll(delta, "units")
        first, last = self.matrix_tree.yview()
        if self.v_scrollbar is not None:
            self.v_scrollbar.set(first, last)
        return "break"

    def _on_mousewheel_linux(self, event: tk.Event) -> str:
        """Scroll both trees together with mouse wheel on Linux/X11."""
        if self.info_tree is None or self.matrix_tree is None:
            return "break"
        if event.num == 4:
            delta = -5
        elif event.num == 5:
            delta = 5
        else:
            delta = 0
        if delta != 0:
            self.info_tree.yview_scroll(delta, "units")
            self.matrix_tree.yview_scroll(delta, "units")
        first, last = self.matrix_tree.yview()
        if self.v_scrollbar is not None:
            self.v_scrollbar.set(first, last)
        return "break"

    # ------------------------------------------------------------------
    # Horizontal mouse wheel (Shift + wheel)
    # ------------------------------------------------------------------

    def _on_hmousewheel(self, event: tk.Event) -> str:
        """Horizontal scroll on matrix using Shift + MouseWheel (Windows/macOS)."""
        if self.matrix_tree is None:
            return "break"

        delta = 0
        if event.delta != 0:
            # Positive delta → scroll left, negative → right (feel free to invert)
            delta = -1 * int(event.delta / 120)

        if delta != 0:
            self.matrix_tree.xview_scroll(delta, "units")

        return "break"

    def _on_hmousewheel_linux(self, event: tk.Event) -> str:
        """Horizontal scroll on matrix using Shift + wheel on Linux/X11."""
        if self.matrix_tree is None:
            return "break"

        if event.num == 4:
            delta = -1  # scroll left
        elif event.num == 5:
            delta = 1  # scroll right
        else:
            delta = 0

        if delta != 0:
            self.matrix_tree.xview_scroll(delta, "units")

        return "break"

    # ------------------------------------------------------------------
    # Info-tree in-place editing
    # ------------------------------------------------------------------

    def _on_info_double_click(self, event: tk.Event) -> None:
        """Start in-place editing of ID / caption / function."""
        if self._is_building or self.info_tree is None:
            return

        region = self.info_tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.info_tree.identify_row(event.y)
        col_id = self.info_tree.identify_column(event.x)
        if not row_id or not col_id:
            return

        try:
            col_index = int(col_id.replace("#", "")) - 1
        except ValueError:
            return

        if col_index < 0 or col_index >= len(self.fixed_columns):
            return

        col_name = self.fixed_columns[col_index]
        if col_name not in ("index", "caption", "func", "midi"):
            # Only those three are editable
            return

        self._begin_info_cell_edit(row_id, col_name)

    def _begin_info_cell_edit(self, item_id: str, col_name: str) -> None:
        """Create a temporary Entry widget over a given cell."""
        if self.info_tree is None:
            return

        # Destroy any previous editor
        editor = getattr(self, "_info_cell_editor", None)
        if editor is not None:
            try:
                editor.destroy()
            except Exception:  # noqa: BLE001
                pass
            self._info_cell_editor = None

        col_index = self.fixed_columns.index(col_name)
        col_id = f"#{col_index + 1}"
        bbox = self.info_tree.bbox(item_id, col_id)
        if not bbox:
            return

        x, y, width, height = bbox
        old_value = self.info_tree.set(item_id, col_name)

        entry = tk.Entry(self.info_tree)
        entry.insert(0, old_value)
        entry.select_range(0, tk.END)
        entry.focus()

        def finish(commit: bool = True) -> None:
            val = entry.get()
            entry.destroy()
            self._info_cell_editor = None
            if commit:
                self._apply_info_cell_edit(item_id, col_name, val)

        entry.bind("<Return>", lambda e: finish(True))
        entry.bind("<KP_Enter>", lambda e: finish(True))
        entry.bind("<Escape>", lambda e: finish(False))
        entry.bind("<FocusOut>", lambda e: finish(True))

        entry.place(x=x, y=y, width=width, height=height)
        self._info_cell_editor = entry

    def _apply_info_cell_edit(
        self,
        item_id: str,
        col_name: str,
        raw_value: str,
    ) -> None:
        """Apply a committed edit to the underlying data model."""
        if self.info_tree is None:
            return

        new_value = raw_value.strip()
        row_index = self.info_tree.index(item_id)
        if row_index < 0 or row_index >= len(self.rows):
            return

        row = self.rows[row_index]
        w = row.primary

        # --- ID column -------------------------------------------------
        if col_name == "index":
            if not new_value:
                return
            try:
                new_id = int(new_value)
            except ValueError:
                # invalid ID -> ignore
                return

            old_id = row.id
            if new_id == old_id:
                return

            # Enforce uniqueness: swap IDs if new_id already exists
            other_row = None
            for r in self.rows:
                if r.id == new_id:
                    other_row = r
                    break

            if other_row is None:
                row.id = new_id
            else:
                other_row.id, row.id = row.id, other_row.id

            self.dirty = True
            self.rebuild_trees()
            return

        # --- Caption ---------------------------------------------------
        if col_name == "caption":
            old_caption = w.caption
            if new_value == old_caption:
                return

            # Update all widgets in the group that currently share this caption
            for gw in row.group:
                if gw.caption == old_caption:
                    gw.caption = new_value
                    gw.element.set("Caption", new_value)

            # If row name is based on caption (no function), keep it in sync
            if not w.func_name and row.name == (old_caption or "(Unnamed)"):
                row.name = new_value or "(Unnamed)"

            self.info_tree.set(item_id, "caption", new_value)
            self._autosize_info_columns()
            self.dirty = True
            return

        # --- Function name ---------------------------------------------
        if col_name == "func":
            # Only Buttons have functions
            if w.widget_type != "Button":
                return

            old_name = w.func_name
            if new_value == old_name:
                return

            w.func_name = new_value
            self.info_tree.set(item_id, "func", new_value)

            # Backend: rename <Function Name="..."> in the Engine
            func_id = getattr(w, "func_id", None)
            workspace = getattr(self, "workspace", None)
            if func_id and workspace is not None and hasattr(workspace, "rename_function_by_id"):
                workspace.rename_function_by_id(func_id, new_value)

            # Keep logical row name in sync if it matched the old function name
            if row.name == old_name:
                row.name = new_value or (w.caption or "(Unnamed)")

            self._autosize_info_columns()
            self.dirty = True
            return

        # --- MIDI ------------------------------------------------------------
        if col_name == "midi":
            if not new_value:
                encoded: int | None = None
            else:
                try:
                    midi_num = int(new_value)
                except ValueError:
                    return
                if not (0 <= midi_num <= 127):
                    return

                encoded = encode_qlc_input_channel(
                    w.widget_type,
                    midi_num,
                    previous=w.midi_channel,
                )

            # update the widgets for this row (store RAW QLC channel)
            for gw in row.group:
                gw.midi_channel = encoded

            self.set_widget_channel(row.primary, encoded)
            self.dirty = True
            self.rebuild_trees()
            return
