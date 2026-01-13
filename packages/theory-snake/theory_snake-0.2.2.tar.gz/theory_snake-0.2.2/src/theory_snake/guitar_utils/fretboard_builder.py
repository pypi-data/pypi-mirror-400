from .string_builder import build_guitar_string

def build_fretboard(tuning):
    """Builds a fretboard for a guitar given its tuning."""
    fretboard = {}
    for open_note in tuning:
        guitar_string = build_guitar_string(open_note)
        if open_note in fretboard:
            duplicate_count = 1
            new_open_note = f"{open_note}_{duplicate_count}"
            while new_open_note in fretboard:
                duplicate_count += 1
                new_open_note = f"{open_note}{duplicate_count}"
            fretboard[new_open_note] = guitar_string
        else:
            fretboard[open_note] = guitar_string
    return fretboard
