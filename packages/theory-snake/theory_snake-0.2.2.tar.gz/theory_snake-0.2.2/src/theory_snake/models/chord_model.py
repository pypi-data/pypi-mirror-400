class Chord:
    def __init__(self, root:str, chord_type:str, notes:list):
        self.root = root
        self.chord_type = chord_type
        self.notes = notes

    def __info__(self):
        return f"Root: {self.root}, Type: {self.chord_type}, Notes: {self.notes}"


class GuitarChord(Chord):
    def __init__(self,chord:Chord, chord_notes:dict):
        self.root = chord.root,
        self.chord_type = chord.chord_type
        self.notes = chord.notes
        self.chord_notes = chord_notes

    def __info__(self):
        return f"Root: {self.root}, Type: {self.chord_type}, Notes: {self.notes}, Guitar Chord Positions: {self.chord_notes}"
