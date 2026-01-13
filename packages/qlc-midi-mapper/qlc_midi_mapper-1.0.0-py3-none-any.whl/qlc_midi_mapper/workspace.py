#!/usr/bin/env python3
"""Backend logic for the QLC+ MIDI routing matrix editor.

This module provides :class:`~workspace.MidiWorkspace`, an in-memory
representation of a QLC+ Workspace (``.qxw``) focused on Virtual Console MIDI
routing.

Features:
- Load / parse a QLC+ Workspace XML file.
- Discover Virtual Console Buttons / Sliders and their MIDI mappings.
- Group widgets into logical rows (:class:`models.RowEntry`).
- Apply updated mappings back into the XML tree.
- Export / import mappings as CSV files.
- Export note-name maps for Studio One and Reaper.

The GUI uses this backend to avoid mixing XML manipulation with Tkinter code.
"""

from __future__ import annotations

import csv

# Use stdlib ElementTree for element creation / SubElement / tostring.
# defusedxml's ElementTree module does not expose Element/SubElement.
import xml.etree.ElementTree as ET
from collections import OrderedDict
from typing import TYPE_CHECKING

# Use defusedxml ONLY for parsing/untrusted XML input.
from defusedxml import ElementTree as DefusedET

if TYPE_CHECKING:
    import xml.etree.ElementTree as StdET

from qlc_midi_mapper.models import RowEntry, VCWidget

QLC_NS = "http://www.qlcplus.org/Workspace"
NS = {"q": QLC_NS}


def _strip_ns(tag: str) -> str:
    """Strip XML namespace from a tag name.

    Args:
        tag: XML tag name potentially containing a namespace.

    Returns:
        The tag without namespace information.
    """
    if "}" in tag:
        return tag.split("}", maxsplit=1)[1]
    return tag


# ---------------------------------------------------------------------------
# QLC+ MIDI "Input Channel" encoding helpers
#
# QLC+ remaps different MIDI message types into a single sequential "Channel"
# number to avoid collisions (CC vs Notes vs Program Change).
#
# QLC+ Input Channel map:
#
# - Control Change (CC) 0..127  -> 128..255
# - Note On/Off         0..127 -> 129..256
#
# QLC+ may additionally add multiples of 4096 internally for MIDI channel /
# OMNI encoding. These upper blocks must be preserved when remapping inputs.
# ---------------------------------------------------------------------------


QLC_CC_BASE = 128
QLC_NOTE_BASE = 129
QLC_OMNI_STRIDE = 4096


def qlc_kind_base(widget_type: str) -> int:
    """Return the QLC+ base for a widget type (Slider->CC, Button->NOTE)."""
    return QLC_NOTE_BASE if widget_type == "Button" else QLC_CC_BASE


def decode_qlc_input_channel(channel: int, widget_type: str) -> tuple[int, int]:
    """Decode a QLC+ input channel into (midi_channel_block, midi_number).

    Returns:
        midi_channel_block: the upper 4096-multiple part (0 if not used)
        midi_number: 0..127 when decodable, otherwise the raw low value.
    """
    high = (int(channel) // QLC_OMNI_STRIDE) * QLC_OMNI_STRIDE
    low = int(channel) % QLC_OMNI_STRIDE
    base = qlc_kind_base(widget_type)
    midi_num = low - base
    return high, midi_num


def encode_qlc_input_channel(widget_type: str, midi_number: int, previous: int | None = None) -> int:
    """Encode (widget_type, midi_number) into a QLC+ input channel.

    Preserves any existing 4096-block (OMNI/channel encoding) from *previous*.
    """
    base = qlc_kind_base(widget_type)
    prev = 0 if previous is None else int(previous)
    high = (prev // QLC_OMNI_STRIDE) * QLC_OMNI_STRIDE
    return high + base + int(midi_number)


class MidiWorkspace:
    """QLC+ workspace backend (no GUI).

    The class parses a ``.qxw`` file and caches Virtual Console widgets
    (Buttons/Sliders) along with their optional MIDI input channels.
    """

    def __init__(self) -> None:
        """Create an empty workspace container."""
        # defusedxml returns stdlib-compatible ElementTree/Element objects,
        # so typing against stdlib ET is correct.
        self.tree: StdET.ElementTree | None = None
        self.root: StdET.Element | None = None
        self.path: str | None = None

        self.widgets: list[VCWidget] = []
        self.rows: list[RowEntry] = []
        self.functions_by_id: dict[str, str] = {}

    @property
    def is_loaded(self) -> bool:
        """Whether a workspace is currently loaded."""
        return self.root is not None

    def load(self, path: str) -> None:
        """Load and parse a QLC+ workspace file from disk.

        Args:
            path: Path to the ``.qxw`` file.
        """
        tree = DefusedET.parse(path)
        root = tree.getroot()

        self.tree = tree
        self.root = root
        self.path = path

        self._index_functions()
        self._collect_widgets()

    def save(self, path: str) -> None:
        """Apply mappings back to XML and save workspace to disk.

        Args:
            path: Destination path for the saved ``.qxw`` file.

        Raises:
            RuntimeError: If no workspace is loaded.
        """
        if self.root is None:
            raise RuntimeError("No workspace loaded")

        self._apply_mappings_to_xml()

        xml_body = ET.tostring(self.root, encoding="unicode")
        header = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE Workspace>\n'
        content = header + xml_body

        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)

    def export_mapping_csv(self, path: str) -> None:
        """Export the current mapping as a CSV file.

        The CSV contains both the displayed CC (``decoded MIDI#/type``) and the
        real QLC channel (as stored in the XML).

        Args:
            path: Destination CSV path.
                channel (see QLC+ channel map).

        Raises:
            RuntimeError: If no widgets were found.
        """
        if not self.rows:
            raise RuntimeError("No widgets in workspace - nothing to export")

        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh, delimiter=",")
            writer.writerow(["Name", "Type", "MIDI#", "QLC_InputChannel", "Caption", "Function", "Path"])

            for row in self.rows:
                widget = row.primary
                if widget.midi_channel is None:
                    continue

                real_ch = int(widget.midi_channel)
                _, midi_num = decode_qlc_input_channel(real_ch, widget.widget_type)
                kind = "NOTE" if widget.widget_type == "Button" else "CC"
                writer.writerow(
                    [
                        row.name,
                        kind,
                        midi_num,
                        real_ch,
                        widget.caption or "",
                        widget.func_name or "",
                        widget.path or "",
                    ]
                )

    def export_studio_one(self, path: str) -> None:
        """Export a Studio One Pitch Name List.

        Studio One uses an XML pitch-name file of the form::

            <Music.PitchNameList>
                <Music.PitchName pitch="0" name="..."/>
            </Music.PitchNameList>

        Args:
            path: Destination file path (commonly ``.pitchlist``).

        Raises:
            RuntimeError: If no widgets were found.
        """
        if not self.rows:
            raise RuntimeError("No widgets in workspace - nothing to export")

        pitch_map: dict[int, str] = {}
        for row in self.rows:
            widget = row.primary
            if widget.midi_channel is None or widget.widget_type != "Button":
                continue

            _, pitch = decode_qlc_input_channel(int(widget.midi_channel), widget.widget_type)
            if 0 <= pitch <= 127:
                pitch_map[pitch] = row.name

        # defusedxml.ElementTree doesn't provide Element/SubElement -> use stdlib ET here.
        root = ET.Element("Music.PitchNameList")
        for pitch in sorted(pitch_map):
            elem = ET.SubElement(root, "Music.PitchName")
            elem.set("pitch", str(pitch))
            elem.set("name", pitch_map[pitch])

        # Pretty-print
        ET.indent(root, space="    ", level=0)

        xml_body = ET.tostring(root, encoding="unicode")
        content = f'<?xml version="1.0"?>\n{xml_body}\n'

        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)

    def export_reaper(self, path: str) -> None:
        """Export a Reaper MIDI note name map.

        The format is a simple tab-separated list::

            // comment
            83    CHOKE ALL CYMBALS

        Args:
            path: Destination text file.

        Raises:
            RuntimeError: If no widgets were found.
        """
        if not self.rows:
            raise RuntimeError("No widgets in workspace - nothing to export")

        note_map: dict[int, str] = {}
        for row in self.rows:
            widget = row.primary
            if widget.midi_channel is None or widget.widget_type != "Button":
                continue

            _, note = decode_qlc_input_channel(int(widget.midi_channel), widget.widget_type)
            if 0 <= note <= 127:
                note_map[note] = row.name

        with open(path, "w", encoding="utf-8") as fh:
            fh.write("// MIDI note name map generated by QLC+ MIDI routing matrix editor\n")
            for note in sorted(note_map):
                fh.write(f"{note}\t{note_map[note]}\n")

    def import_mapping_csv(self, path: str) -> tuple[int, list[str]]:
        """Import a mapping CSV and apply it to the current workspace.

        The CSV must contain at least a ``Name`` column plus either ``CC`` or
        ``Channel`` (real channel). If ``CC`` is provided, it is converted to
        the real channel using the QLC+ channel map.

        Args:
            path: CSV file to read.

        Returns:
            A tuple ``(applied_rows, unknown_names)`` where:
                - ``applied_rows`` is the number of logical names applied.
                - ``unknown_names`` lists CSV names not found in the workspace.

        Raises:
            RuntimeError: If no workspace has been loaded.
            ValueError: If the CSV header is missing required columns.
        """
        if not self.rows:
            raise RuntimeError("No workspace loaded - cannot import mapping")

        with open(path, encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                raise ValueError("CSV has no header row.")

            fieldnames = [field.strip() for field in reader.fieldnames]

            name_field: str | None = None
            type_field: str | None = None
            midi_field: str | None = None
            qlc_field: str | None = None

            for field in fieldnames:
                low = field.lower()
                if low == "name":
                    name_field = field
                elif low in ("type", "kind"):
                    type_field = field
                elif low in ("midi#", "midi", "midinumber", "number", "cc"):
                    midi_field = field
                elif low in ("qlc_inputchannel", "qlc_channel", "qlcinputchannel", "inputchannel", "channel"):
                    qlc_field = field

            if name_field is None or (midi_field is None and qlc_field is None):
                raise ValueError(
                    "CSV must contain at least: Name + (MIDI# or QLC_InputChannel). "
                    "Recommended columns: Name, Type, MIDI#, QLC_InputChannel."
                )

            name_to_widgets: dict[str, list[VCWidget]] = {}
            for row in self.rows:
                name_to_widgets.setdefault(row.name, []).extend(row.group)

            applied_rows = 0
            unknown_names: list[str] = []

            for csv_row in reader:
                raw_name = csv_row.get(name_field, "")
                if raw_name is None:
                    continue

                name = raw_name.strip()
                if not name:
                    continue

                raw_type = (csv_row.get(type_field, "") or "").strip() if type_field else ""
                raw_midi = (csv_row.get(midi_field, "") or "").strip() if midi_field else ""
                raw_qlc = (csv_row.get(qlc_field, "") or "").strip() if qlc_field else ""

                # Optional filters from CSV (Type column):
                # - "CC" applies to Sliders
                # - "NOTE" applies to Buttons
                type_filter = raw_type.upper()

                midi_num: int | None = None
                if raw_midi != "":
                    try:
                        midi_num = int(raw_midi)
                    except ValueError:
                        midi_num = None

                qlc_channel: int | None = None
                if raw_qlc != "":
                    try:
                        qlc_channel = int(raw_qlc)
                    except ValueError:
                        qlc_channel = None
                widgets_for_name = name_to_widgets.get(name)
                if not widgets_for_name:
                    unknown_names.append(name)
                    continue

                for widget in widgets_for_name:
                    # Apply optional Type filter from the CSV row, if present
                    if type_filter in ("CC", "FADER") and widget.widget_type == "Button":
                        continue
                    if type_filter in ("NOTE", "BUTTON") and widget.widget_type != "Button":
                        continue

                    if qlc_channel is not None:
                        widget.midi_channel = qlc_channel
                    elif midi_num is not None and 0 <= midi_num <= 127:
                        widget.midi_channel = encode_qlc_input_channel(
                            widget.widget_type,
                            midi_num,
                            previous=widget.midi_channel,
                        )
                    else:
                        widget.midi_channel = None
                applied_rows += 1

        return applied_rows, sorted(set(unknown_names))

    def rename_function_by_id(self, func_id: str, new_name: str) -> None:
        """Rename a QLC+ Function and update all cached widgets that use it.

        Args:
            func_id: The QLC+ function ID.
            new_name: New function name (empty string removes cached entry).
        """
        if self.root is None:
            return

        engine = self.root.find("q:Engine", NS)
        if engine is not None:
            for func_elem in engine.findall("q:Function", NS):
                if func_elem.get("ID") == func_id:
                    func_elem.set("Name", new_name)
                    break

        if new_name:
            self.functions_by_id[func_id] = new_name
        else:
            self.functions_by_id.pop(func_id, None)

        for widget in self.widgets:
            if widget.func_id == func_id:
                widget.func_name = new_name

    def _exported_name(self, widget: VCWidget) -> str:
        """Return the exported name used to group widgets."""
        return widget.func_name or widget.caption or "(Unnamed)"

    def _index_functions(self) -> None:
        """Index Engine functions by ID to resolve Button function names."""
        self.functions_by_id.clear()
        if self.root is None:
            return

        engine = self.root.find("q:Engine", NS)
        if engine is None:
            return

        for func_elem in engine.findall("q:Function", NS):
            func_id = func_elem.get("ID")
            func_name = func_elem.get("Name", "")
            if func_id and func_name:
                self.functions_by_id[func_id] = func_name

    def _collect_widgets(self) -> None:
        """Collect Virtual Console widgets and build logical rows."""
        self.widgets.clear()
        self.rows.clear()

        if self.root is None:
            return

        vc_elem = self.root.find("q:VirtualConsole", NS)
        if vc_elem is None:
            return

        index_counter = 0

        def walk_frames(elem: StdET.Element, path_prefix: str) -> None:
            nonlocal index_counter

            tag = _strip_ns(elem.tag)
            caption = elem.get("Caption", "")

            if tag in {"Frame", "SoloFrame"}:
                new_prefix = caption if not path_prefix else f"{path_prefix}/{caption}"
                for child in list(elem):
                    walk_frames(child, new_prefix)
                return

            if tag in {"Button", "Slider"}:
                widget_type = tag
                w_caption = elem.get("Caption", "")
                if tag == "Button":
                    func_id, func_name = self._get_widget_function_info(elem)
                else:
                    func_id, func_name = None, ""
                midi_channel = self._get_widget_midi_channel(elem)

                vc_widget = VCWidget(
                    index=index_counter,
                    element=elem,
                    widget_type=widget_type,
                    caption=w_caption,
                    func_id=func_id,
                    func_name=func_name,
                    path=path_prefix,
                    midi_channel=midi_channel,
                )
                self.widgets.append(vc_widget)
                index_counter += 1
                return

            for child in list(elem):
                walk_frames(child, path_prefix)

        walk_frames(vc_elem, "")
        self._build_rows_from_widgets()

    def _build_rows_from_widgets(self) -> None:
        """Group widgets into logical rows based on exported name."""
        groups: OrderedDict[str, list[VCWidget]] = OrderedDict()
        for widget in self.widgets:
            name = self._exported_name(widget)
            groups.setdefault(name, []).append(widget)

        self.rows = []
        for name, widgets in groups.items():
            primary = widgets[0]
            for extra in widgets[1:]:
                extra.midi_channel = primary.midi_channel

            row_id = primary.index
            self.rows.append(RowEntry(id=row_id, name=name, primary=primary, group=widgets))

    @staticmethod
    def _get_widget_midi_channel(elem: StdET.Element) -> int | None:
        """Return the MIDI channel from the widget's ``<Input>`` element."""
        input_elem = elem.find("q:Input", NS)
        if input_elem is None:
            return None

        ch_str = input_elem.get("Channel")
        if ch_str is None:
            return None

        try:
            return int(ch_str)
        except ValueError:
            return None

    def _apply_mappings_to_xml(self) -> None:
        """Apply cached widget MIDI channels back into the XML tree."""
        for widget in self.widgets:
            elem = widget.element
            input_elem = elem.find("q:Input", NS)

            if widget.midi_channel is None:
                if input_elem is not None:
                    elem.remove(input_elem)
                continue

            if input_elem is None:
                input_elem = ET.SubElement(elem, f"{{{QLC_NS}}}Input")
                input_elem.set("ID", "0")
                input_elem.set("Universe", "0")

            input_elem.set("Channel", str(widget.midi_channel))

    def _get_widget_function_info(self, btn_elem: StdET.Element) -> tuple[str | None, str]:
        """Return the function ID and name for a Button widget.

        Args:
            btn_elem: The ``<Button>`` XML element.

        Returns:
            A tuple ``(func_id, func_name)``. If the button has no function,
            ``func_id`` is ``None`` and ``func_name`` is an empty string.
        """
        func_elem = btn_elem.find("q:Function", NS)
        if func_elem is None:
            return None, ""

        func_id = func_elem.get("ID")
        if func_id is None:
            return None, ""

        return func_id, self.functions_by_id.get(func_id, "")
