#Notes
Notes = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

#Scale Intervals
MAJOR_SCALE_INTERVALS = [2, 2, 1, 2, 2, 2, 1]
MINOR_SCALE_INTERVALS = [2, 1, 2, 2, 1, 2, 2]

# Chord Types
MAJOR_CHORD = ['1','3','5']
MINOR_CHORD = ['1','3b','5']

#Guitar constants
FRET_COUNT = 18
COMMON_TUNNINGS = {
    "Standard": ["E", "A", "D", "G", "B", "E"],
    "Drop D": ["D", "A", "D", "G", "B", "E"],
    "DADGAD": ["D", "A", "D", "G", "A", "D"],
    "Open G": ["D", "G", "D", "G", "B", "D"],
    "Open D": ["D", "A", "D", "F#", "A", "D"],
}

__info__  = f"""
    Notes: {Notes}

    Supported Intervals:
        - Major Scale Intervals (major)
        - Minor Scale Intervals (minor)

    Supported Chord Types:
        - Major Chord
        - Minor Chord

    Supported Guitar Tunings:
        - Standard
        - Drop D
        - DADGAD
        - Open G
        - Open D
    """

