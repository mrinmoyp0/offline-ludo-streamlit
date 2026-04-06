# Offline Ludo

A local multiplayer Ludo game built with Streamlit.

The gameplay rules live in Python, while the board itself is rendered by a custom HTML/CSS/JS Streamlit component. It supports offline play for 2, 3, or 4 people on the same device.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Features

- Offline local play for 2, 3, or 4 players
- Custom board renderer built with HTML, CSS, and JavaScript
- Python game engine for turns, dice rolls, captures, safe squares, home lanes, and win detection
- Clickable token movement directly on the board
- Player setup panel for names and player count
- Match history and per-player token summaries

## Rules Implemented

- A token needs a 6 to leave the yard
- Exact rolls are required to reach home
- Safe star squares cannot be used for captures
- Captures send opponents back to their yard
- Rolling a 6, capturing a token, or reaching home grants another roll
- Three consecutive sixes forfeit the turn

## Tests

```bash
python -m unittest discover -s tests
```
