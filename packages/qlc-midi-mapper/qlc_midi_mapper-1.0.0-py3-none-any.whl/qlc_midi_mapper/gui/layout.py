#!/usr/bin/env python3
"""Main layout (widgets, frames, treeviews) for the MIDI matrix GUI.

This module focuses exclusively on creating and arranging the widgets.
All behaviors (events, sorting, editing) live in other mixins.
"""


from qlc_midi_mapper.gui.base import DND_AVAILABLE, DND_FILES, tk, tkfont, ttk


class LayoutMixin:
    """Mixin that builds the main GUI layout."""

    fixed_columns: list[str]
    cc_columns: list[str]

    def _create_main_layout(self) -> None:
        """Create the main layout of the window."""
        # Fixed columns for the left info tree (kept in sync with EventsMixin row values)
        self.fixed_columns = ["index", "type", "caption", "func", "path", "midi"]

        # 128 matrix columns representing MIDI numbers 0–127
        # Internally stored as cc_0 .. cc_127
        self.cc_columns = [f"cc_{i}" for i in range(128)]
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            # Theme not available on some platforms.
            pass

        # Top controls frame
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)

        # File controls
        open_btn = ttk.Button(
            top_frame,
            text="Open QLC Workspace...",
            command=self.open_workspace,
        )
        open_btn.pack(side=tk.LEFT, padx=(0, 4))

        import_btn = ttk.Button(
            top_frame,
            text="Import Mapping CSV...",
            command=self.import_mapping_csv,
        )
        import_btn.pack(side=tk.LEFT, padx=4)

        save_btn = ttk.Button(
            top_frame,
            text="Save Workspace As...",
            command=self.save_workspace_as,
        )
        save_btn.pack(side=tk.LEFT, padx=4)

        self.export_csv = tk.IntVar(value=1)
        self.export_studio_one = tk.IntVar(value=1)
        self.export_reaper = tk.IntVar(value=1)

        export_csv_cb = ttk.Checkbutton(
            top_frame,
            text="Export CSV mapping",
            variable=self.export_csv,
        )
        export_studio_one_cb = ttk.Checkbutton(
            top_frame,
            text="Export Studio One Mapping",
            variable=self.export_studio_one,
        )
        export_reaper_cb = ttk.Checkbutton(
            top_frame,
            text="Export Reaper Mapping",
            variable=self.export_reaper,
        )

        export_csv_cb.pack(side=tk.LEFT, padx=(4, 20))
        export_studio_one_cb.pack(side=tk.LEFT, padx=(4, 20))
        export_reaper_cb.pack(side=tk.LEFT, padx=(4, 20))

        # Status label
        status_label = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status_label.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(0, 4))

        # Main frame containing the two treeviews
        main_frame = ttk.Frame(self)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Left (info) frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Vertical separator between info and matrix
        sep = ttk.Separator(main_frame, orient="vertical")
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=4)

        # Right (matrix) frame
        matrix_frame = ttk.Frame(main_frame)
        matrix_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Styles for grid-like appearance
        style.configure(
            "Info.Treeview",
            rowheight=22,
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Matrix.Treeview",
            rowheight=22,
            borderwidth=1,
            relief="solid",
        )

        # Selected row highlight.
        style.map("Matrix.Treeview", background=[("selected", "#cde6ff")])

        style.configure(
            "Matrix.Heading",
            borderwidth=1,
            bordercolor="black",
            relief="solid",
        )
        style.configure(
            "Matrix.HighlightHeading",
            borderwidth=1,
            bordercolor="black",
            relief="solid",
        )

        # Left tree: fixed columns
        self.info_tree = ttk.Treeview(
            info_frame,
            columns=self.fixed_columns,
            show="headings",
            selectmode="browse",
            height=20,
            style="Info.Treeview",
        )
        self.info_tree.pack(side=tk.LEFT, fill=tk.Y)

        self.info_tree.heading("index", text="#")
        self.info_tree.heading("type", text="Type")
        self.info_tree.heading("caption", text="Caption")
        self.info_tree.heading("func", text="Function")
        self.info_tree.heading("path", text="Path")
        self.info_tree.heading("midi", text="MIDI #")

        self.info_tree.column("index", width=40, anchor=tk.CENTER, stretch=False)
        self.info_tree.column("type", width=70, anchor=tk.CENTER, stretch=False)
        self.info_tree.column("caption", width=200, anchor=tk.W, stretch=True)
        self.info_tree.column("func", width=200, anchor=tk.W, stretch=True)
        self.info_tree.column("path", width=260, anchor=tk.W, stretch=True)
        self.info_tree.column("midi", width=80, anchor=tk.CENTER, stretch=False)

        # Right tree: matrix (CC columns)
        self.matrix_tree = ttk.Treeview(
            matrix_frame,
            columns=(),
            show="headings",
            selectmode="browse",
            style="Matrix.Treeview",
        )
        self.matrix_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Shared vertical scrollbar
        def _on_vscroll(*args: str) -> None:
            if self.info_tree is not None:
                self.info_tree.yview(*args)
            if self.matrix_tree is not None:
                self.matrix_tree.yview(*args)

        self.v_scrollbar = ttk.Scrollbar(
            main_frame,
            orient="vertical",
            command=_on_vscroll,
        )
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.info_tree.configure(yscrollcommand=self.v_scrollbar.set)
        self.matrix_tree.configure(yscrollcommand=self.v_scrollbar.set)

        # Horizontal scrollbar for matrix only
        h_scrollbar = ttk.Scrollbar(
            matrix_frame,
            orient="horizontal",
            command=self.matrix_tree.xview,
        )
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.matrix_tree.configure(xscrollcommand=h_scrollbar.set)

        # Configure CC columns initially
        self._configure_matrix_columns()

        # Sorting handlers for info-tree headings
        self._setup_info_heading_sort_handlers()

        # Selection sync
        self.info_tree.bind("<<TreeviewSelect>>", self._on_info_select)
        self.matrix_tree.bind("<<TreeviewSelect>>", self._on_matrix_select)

        # In-place editing on the left tree (ID / caption / function)
        self.info_tree.bind("<Double-1>", self._on_info_double_click)

        # Matrix click handlers
        self.matrix_tree.bind("<Button-1>", self.on_matrix_click)
        self.matrix_tree.bind("<Double-1>", self.on_matrix_double_click)

        # Mouse wheel scroll sync (vertical)
        self.info_tree.bind("<MouseWheel>", self._on_mousewheel)
        self.matrix_tree.bind("<MouseWheel>", self._on_mousewheel)
        self.info_tree.bind("<Button-4>", self._on_mousewheel_linux)
        self.info_tree.bind("<Button-5>", self._on_mousewheel_linux)
        self.matrix_tree.bind("<Button-4>", self._on_mousewheel_linux)
        self.matrix_tree.bind("<Button-5>", self._on_mousewheel_linux)

        # Mouse wheel scroll (horizontal: Shift + wheel → horizontal scroll on matrix)
        self.matrix_tree.bind("<Shift-MouseWheel>", self._on_hmousewheel)
        self.matrix_tree.bind("<Shift-Button-4>", self._on_hmousewheel_linux)
        self.matrix_tree.bind("<Shift-Button-5>", self._on_hmousewheel_linux)

        # Drag & drop on main widgets
        if DND_AVAILABLE:
            widgets = [
                main_frame,
                info_frame,
                matrix_frame,
                self.info_tree,
                self.matrix_tree,
            ]
            for widget in widgets:
                try:
                    widget.drop_target_register(DND_FILES)  # type: ignore[attr-defined]
                    widget.dnd_bind(
                        "<<Drop>>",
                        self._on_drop_files,
                    )  # type: ignore[attr-defined]
                except Exception:
                    # Some widgets / platforms may not support this cleanly.
                    pass

    def _autosize_info_columns(self) -> None:
        """Resize left columns width based on their content."""
        if self.info_tree is None:
            return

        font = tkfont.nametofont("TkDefaultFont")
        padding = 16

        for col in self.fixed_columns:
            header = self.info_tree.heading(col, "text")
            max_width = font.measure(header)

            for item in self.info_tree.get_children(""):
                val = str(self.info_tree.set(item, col))
                width = font.measure(val)
                max_width = max(max_width, width)

            if col == "index":
                min_width = 40
            elif col == "midi":
                min_width = 80
            else:
                min_width = 120

            final_width = max(min_width, max_width + padding)
            self.info_tree.column(
                col,
                width=final_width,
                stretch=col not in ("index", "midi"),
            )
