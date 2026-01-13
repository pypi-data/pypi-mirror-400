"""Unit tests for the QLC+ MIDI routing matrix backend.

These tests validate the behavior of :class:`qlc_midi_mapper.workspace.MidiWorkspace`
against a minimal but representative QLC+ workspace XML (``.qxw``) that includes:

- Engine Functions (to resolve button function names)
- Virtual Console widgets (Buttons/Sliders)
- Nested Frames / SoloFrames (to build widget paths)
- MIDI Input mapping via ``<Input Channel="...">``

Important:
QLC+ encodes MIDI mappings into a single integer "Input Channel" space:

- CC 0..127   -> 1..128
- NOTE 0..127 -> 129..256

(Some QLC+ configurations additionally encode MIDI channel / omni selection by adding
multiples of 4096; this suite preserves any existing 4096-block when re-encoding.)

The backend therefore exposes:
- widget.midi_channel as the raw QLC+ Input Channel integer
- CSV exports a decoded MIDI number (0..127) + Type (CC vs NOTE)

Fixture expectation:
The minimal test workspace used by the `workspace` fixture must use the QLC+ block
encoding above. In particular, if you previously used an offset-based encoding like
"125 + CC", update the fixture so sliders use CC-block values (1..128) and buttons
use NOTE-block values (129..256). For example:
- CC 15  -> Channel="143"
- NOTE 1 -> Channel="130"
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from qlc_midi_mapper.workspace import (
    NS,
    MidiWorkspace,
    _strip_ns,
    decode_qlc_input_channel,
    encode_qlc_input_channel,
)


def test_strip_ns() -> None:
    """Strip namespace prefixes from XML tags."""
    assert _strip_ns("{x}Tag") == "Tag"
    assert _strip_ns("Tag") == "Tag"


def test_load_indexes_functions(workspace: MidiWorkspace) -> None:
    """Loading a workspace should index Engine Functions by ID."""
    assert workspace.is_loaded
    assert workspace.functions_by_id["1"] == "FuncA"
    assert workspace.functions_by_id["2"] == "FuncB"


def test_collect_widgets_and_paths(workspace: MidiWorkspace) -> None:
    """Widget collection should find VC widgets and build correct paths."""
    # Btn1, Btn2, Sld, NoFunc
    assert len(workspace.widgets) == 4

    btn1 = workspace.widgets[0]
    assert btn1.widget_type == "Button"
    assert btn1.caption == "Btn1"
    assert btn1.func_id == "1"
    assert btn1.func_name == "FuncA"
    assert btn1.path == "Main"
    assert btn1.midi_channel == 130  # NOTE 1 -> 129 + 1

    high, note = decode_qlc_input_channel(btn1.midi_channel, btn1.widget_type)
    assert high % 4096 == 0
    assert note == 1

    sld = next(w for w in workspace.widgets if w.widget_type == "Slider")
    assert sld.path == "Main/Sub"
    assert sld.caption == "Sld"
    assert sld.func_id is None
    assert sld.func_name == ""

    # Fixture should encode CC 15 as Channel="143"
    assert sld.midi_channel == 143

    high, cc = decode_qlc_input_channel(sld.midi_channel, sld.widget_type)
    assert high % 4096 == 0
    assert cc == 15


def test_build_rows_groups_by_exported_name(workspace: MidiWorkspace) -> None:
    """Rows should group widgets by exported name and propagate MIDI channels."""
    names = [r.name for r in workspace.rows]
    assert names == ["FuncA", "Sld", "NoFunc"]

    funca_row = workspace.rows[0]
    assert funca_row.name == "FuncA"
    assert len(funca_row.group) == 2
    assert funca_row.primary.caption == "Btn1"

    # Secondary button should inherit primary QLC input channel in cache
    secondary = funca_row.group[1]
    assert secondary.caption == "Btn2"
    assert secondary.midi_channel == funca_row.primary.midi_channel == 130


def test_rename_function_by_id_updates_engine_and_widgets(workspace: MidiWorkspace) -> None:
    """Renaming a function should update XML, index, and cached widget names."""
    funca_row = next(r for r in workspace.rows if r.name == "FuncA")
    assert funca_row.primary.func_name == "FuncA"

    workspace.rename_function_by_id("1", "NewName")

    assert workspace.functions_by_id["1"] == "NewName"
    assert all(w.func_name == "NewName" for w in funca_row.group)

    engine = workspace.root.find("q:Engine", NS)  # type: ignore[union-attr]
    assert engine is not None
    func_elems = engine.findall("q:Function", NS)
    assert any(fe.get("ID") == "1" and fe.get("Name") == "NewName" for fe in func_elems)


def test_apply_mappings_to_xml_and_save_roundtrip(tmp_path: Path, workspace: MidiWorkspace) -> None:
    """Saving should apply mappings back into XML, including removals.

    Note: row ordering can change after reload, so validate per-widget.
    """
    # Remove mapping from slider
    sld_row = next(r for r in workspace.rows if r.name == "Sld")
    sld_row.primary.midi_channel = None

    # Set NOTE number = 2 for both buttons in FuncA group
    funca_row = next(r for r in workspace.rows if r.name == "FuncA")
    new_btn_channel = encode_qlc_input_channel("Button", 2, previous=funca_row.primary.midi_channel)
    for w in funca_row.group:
        w.midi_channel = new_btn_channel

    out = tmp_path / "out.qxw"
    workspace.save(str(out))

    ws2 = MidiWorkspace()
    ws2.load(str(out))

    # Verify both buttons (by caption) are NOTE 2
    btn1_2 = next(w for w in ws2.widgets if w.widget_type == "Button" and w.caption == "Btn1")
    btn2_2 = next(w for w in ws2.widgets if w.widget_type == "Button" and w.caption == "Btn2")

    _, note1 = decode_qlc_input_channel(btn1_2.midi_channel, "Button")
    _, note2 = decode_qlc_input_channel(btn2_2.midi_channel, "Button")
    assert note1 == 2
    assert note2 == 2

    # Slider mapping removed
    sld2 = next(r for r in ws2.rows if r.name == "Sld")
    assert sld2.primary.midi_channel is None


def test_export_mapping_csv(tmp_path: Path, workspace: MidiWorkspace) -> None:
    """CSV export should include decoded Type + MIDI# and the raw QLC input channel."""
    out = tmp_path / "map.csv"
    workspace.export_mapping_csv(str(out))

    rows = list(csv.DictReader(out.read_text(encoding="utf-8").splitlines()))
    assert {r["Name"] for r in rows} == {"FuncA", "Sld", "NoFunc"}

    funca = next(r for r in rows if r["Name"] == "FuncA")
    assert funca["Type"] == "NOTE"
    assert funca["MIDI#"] == "1"
    assert funca["QLC_InputChannel"] == "130"

    sld = next(r for r in rows if r["Name"] == "Sld")
    assert sld["Type"] == "CC"
    assert sld["MIDI#"] == "15"
    assert sld["QLC_InputChannel"] == "143"


def test_import_mapping_csv_midinumber_and_type(tmp_path: Path, workspace: MidiWorkspace) -> None:
    """CSV import should apply MIDI# based on Type and report unknown names."""
    csv_path = tmp_path / "in.csv"
    csv_path.write_text(
        "Name,Type,MIDI#\n" "FuncA,NOTE,7\n" "Sld,CC,10\n" "Unknown,CC,1\n",
        encoding="utf-8",
    )

    applied, unknown = workspace.import_mapping_csv(str(csv_path))
    assert applied == 2
    assert unknown == ["Unknown"]

    funca_row = next(r for r in workspace.rows if r.name == "FuncA")
    expected = encode_qlc_input_channel("Button", 7, previous=funca_row.primary.midi_channel)
    assert all(w.midi_channel == expected for w in funca_row.group)

    sld_row = next(r for r in workspace.rows if r.name == "Sld")
    assert sld_row.primary.midi_channel == encode_qlc_input_channel("Slider", 10, previous=sld_row.primary.midi_channel)


def test_import_mapping_csv_qlc_inputchannel_field(tmp_path: Path, workspace: MidiWorkspace) -> None:
    """CSV import should accept raw QLC input channels via QLC_InputChannel."""
    csv_path = tmp_path / "in2.csv"
    csv_path.write_text(
        "Name,QLC_InputChannel\n" "Sld,20\n",
        encoding="utf-8",
    )

    applied, unknown = workspace.import_mapping_csv(str(csv_path))
    assert applied == 1
    assert unknown == []

    sld_row = next(r for r in workspace.rows if r.name == "Sld")
    assert sld_row.primary.midi_channel == 20


def test_import_mapping_csv_missing_required_columns(tmp_path: Path, workspace: MidiWorkspace) -> None:
    """CSV import should reject files missing Name + (MIDI# or QLC_InputChannel) columns."""
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("Foo,Bar\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError):
        workspace.import_mapping_csv(str(csv_path))


def test_export_studio_one_pitchlist_formatting(tmp_path: Path, workspace: MidiWorkspace) -> None:
    """Pitchlist export should be pretty-printed and contain expected NOTE pitches."""
    out = tmp_path / "map.pitchlist"
    workspace.export_studio_one(str(out))

    text = out.read_text(encoding="utf-8")
    assert text.startswith('<?xml version="1.0"?>\n')
    assert "\n<Music.PitchNameList>" in text
    assert "\n    <Music.PitchName " in text
    assert text.endswith("\n")

    # FuncA button is NOTE 1
    assert 'pitch="1"' in text
    assert "</Music.PitchNameList>" in text


def test_export_reaper_note_map(tmp_path: Path, workspace: MidiWorkspace) -> None:
    """Reaper note-map export should be tab-separated and include expected notes."""
    out = tmp_path / "map.txt"
    workspace.export_reaper(str(out))

    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("// MIDI note name map generated")
    assert any(line.startswith("1\tFuncA") for line in lines[1:])
