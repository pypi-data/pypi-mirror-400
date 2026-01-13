# theory_snake 🐍🎶

A compact, modular Python library for music theory and guitar modeling. It provides utilities for notes, scales, chords, tunings, fretboards, and mapping theoretical chords to playable guitar shapes.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Table of Contents

- [Features](#features)
- [Install](#install)
- [Quick Start](#quick-start)
- [Examples](#examples)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- Note utilities (sharps, flats)
- Scale generation (major, minor)
- Chord modeling and builders
- Guitar utilities: tunings, strings, fretboard builder
- Map theoretical chords to playable guitar shapes

## Install

Install from PyPI:

```
pip install theory-snake
```

Or install from source (editable):

```
pip install -e .
```

## Quick Start

Import core utilities:

```python
from theory_snake import note_utils, scale_builder, chord_utils

# Constants / metadata
from theory_snake import consts
print(consts.__info__)
```

Note utilities:

```python
import theory_snake.note_utils as nu
print(nu.get_sharp("C"))  # C#
print(nu.get_flat("E"))   # D#
```

Scale builder:

```python
import theory_snake.scale_builder as sb
print(sb.build_scale("C", "major"))
print(sb.build_scale("A", "minor"))
```

Chord model & utilities:

```python
from theory_snake.models.chord_model import Chord
from theory_snake import chord_utils as cb

chord = Chord("C", "major", ["C", "E", "G"])
print(chord.__info__())

c_major = cb.build_chord("C", "major")
print(c_major.notes)  # ['C', 'E', 'G']
```

Guitar utilities (tunings, strings, fretboard):

```python
from theory_snake import guitar_utils as gu

tuning = gu.tuning_utils.select_tuning("Standard")
fretboard = gu.fretboard_builder.build_fretboard(tuning)
guitar_string = gu.string_builder.build_guitar_string("E")

c_major = cb.build_chord("C", "major")
guitar_chord = gu.guitar_chord_utils.make_guitar_chord(fretboard, c_major)
print(guitar_chord.__info__())
```

## Project Structure

```
theory_snake/
├── consts.py
├── note_utils.py
├── scale_builder.py
├── chord_utils.py
├── guitar_utils/
│   ├── tuning_utils.py
   │   ├── string_builder.py
   │   ├── fretboard_builder.py
   │   └── guitar_chord_utils.py
└── models/
    └── chord_model.py
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---
