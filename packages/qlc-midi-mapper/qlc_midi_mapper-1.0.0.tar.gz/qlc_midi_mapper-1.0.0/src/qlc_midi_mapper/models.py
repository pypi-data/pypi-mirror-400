#!/usr/bin/env python3

"""Data models for the QLC+ MIDI routing matrix editor."""


from dataclasses import dataclass
from xml.etree.ElementTree import Element  # nosec


@dataclass
class VCWidget:
    """Representation of a Virtual Console widget and its mapping.

    This is used for Buttons and Sliders that can have MIDI <Input>.

    Attributes:
        index: Incremental index used as stable ordering (original order).
        element: XML element corresponding to the widget (<Button> or <Slider>).
        widget_type: Type of widget ("Button" or "Slider").
        caption: Caption of the widget (Caption attribute).
        func_id: ID of the associated Function, if any (for Buttons).
        func_name: Name of the associated Function, if any (for Buttons).
        path: Hierarchical path of Frames/SoloFrames leading to the widget.
        midi_channel: Currently mapped MIDI channel (real QLC channel),
            or None if no mapping is present.
    """

    index: int
    element: Element
    widget_type: str
    caption: str
    func_id: str | None
    func_name: str
    path: str
    midi_channel: int | None


@dataclass
class RowEntry:
    """Row representing one *logical* control in the matrix.

    Multiple VCWidget instances can be grouped under a single row when they
    share the same exported name (caption / function name / fallback).

    Attributes:
        id: User-editable logical ID for this row (shown in "#" column).
        name: Display / CSV name (caption or func name or "(Unnamed)").
        primary: The first VCWidget in the group, used for display.
        group: All VCWidgets belonging to this logical row.
    """

    id: int
    name: str
    primary: VCWidget
    group: list[VCWidget]
