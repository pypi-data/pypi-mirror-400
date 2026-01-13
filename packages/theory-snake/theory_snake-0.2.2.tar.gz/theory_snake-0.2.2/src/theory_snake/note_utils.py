from .consts import Notes

def get_sharp(note):
    """Returns the sharp version of the given note."""
    if note not in Notes:
        raise ValueError("Invalid note")
    index = Notes.index(note)
    sharp_index = (index + 1) % len(Notes)
    return Notes[sharp_index]

def get_flat(note):
    """Returns the flat version of the given note."""
    if note not in Notes:
        raise ValueError("Invalid note")
    index = Notes.index(note)
    flat_index = (index - 1) % len(Notes)
    return Notes[flat_index]


if __name__ == "__main__":
    print(get_sharp("G"))  # Example usage
    print(get_flat("D"))   # Example usage
