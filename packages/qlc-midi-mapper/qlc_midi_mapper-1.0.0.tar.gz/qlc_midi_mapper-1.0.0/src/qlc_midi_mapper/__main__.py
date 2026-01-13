#!/usr/bin/env python3
"""CLI entry point for the QLC+ MIDI routing matrix editor."""


from qlc_midi_mapper.gui.app import MidiMatrixApp


def main() -> None:
    """Run the Tkinter GUI application."""
    app = MidiMatrixApp()
    app.mainloop()


if __name__ == "__main__":
    main()
