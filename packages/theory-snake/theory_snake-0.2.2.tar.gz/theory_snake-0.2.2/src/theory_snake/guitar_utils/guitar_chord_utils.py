from ..models.chord_model import GuitarChord

def make_guitar_chord(fret_board, chord):
    guitar_chord = {}
    for string in fret_board:
        note_list = fret_board[string]
        for note in note_list:
            if note in chord.notes:
                guitar_chord[string] = note_list.index(note)
                break

    guitar_chord_obj = GuitarChord(chord,guitar_chord)

    return guitar_chord_obj
