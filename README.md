# Dino Run

A Python implementation of the classic chrome offline dinosaur game using Pygame.

## Requirements

- Python 3.12+
- Pygame

## Installation

```bash
uv sync
```

## How to Play

Run the game:
```bash
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| SPACE / W / UP | Jump |
| DOWN / S | Duck |
| R | Restart (after game over) |

### Game Features

- Jump and duck mechanics
- Extend jump by holding jump key
- Fast fall by pressing duck while jumping
- Ground cacti and flying birds as obstacles
- High score persistence
- Animated graphics (running dino, flapping birds)
- Background scenery with clouds and mountains

### Game States

1. **Start Screen** - Press SPACE/W/UP to begin
2. **Playing** - Dodge obstacles, survive as long as possible
3. **Game Over** - Press R to restart

## Project Structure

```
.
├── main.py          # Game source code
├── pyproject.toml   # Dependencies
└── highscore.txt   # Saved high score (generated)
```