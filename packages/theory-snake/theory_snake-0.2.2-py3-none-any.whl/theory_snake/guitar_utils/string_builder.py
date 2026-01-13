from ..consts import FRET_COUNT
from ..note_utils import get_sharp

def build_guitar_string(open_note, fret_count=FRET_COUNT):
    """Builds a list of notes for a guitar string given its open note."""
    guitar_string = []
    current_note = open_note
    guitar_string.append(current_note)
    for fret in range(fret_count + 1):
        current_note = get_sharp(current_note)
        guitar_string.append(current_note)
    return guitar_string
