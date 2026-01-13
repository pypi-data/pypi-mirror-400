from .consts import Notes, MAJOR_SCALE_INTERVALS, MINOR_SCALE_INTERVALS

def build_scale(root_note, scale_type):
    scale_type = scale_type.lower()
    match scale_type:
        case 'major':
            intervals = MAJOR_SCALE_INTERVALS
        case 'minor':
            intervals = MINOR_SCALE_INTERVALS
        case _:
            return ValueError("Unsupported scale type")
    scale = [root_note]
    current_index = Notes.index(root_note)
    for interval in intervals:
        current_index = (current_index + interval) % len(Notes)
        scale.append(Notes[current_index])
    return scale

if __name__ == "__main__":
    print(build_scale("C", "major"))  # Example usage
    print(build_scale("C", "minor"))  # Example usage
