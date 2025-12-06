# Chiki's Chase 🐤🐍

_A retro-style chase game where a brave little chick tries to survive against a relentless snake._

This is a Python game built with **Pygame** and a simple **Flask** integration to launch the game from a stylish HTML menu screen.

---

## 🎮 Game Overview

You play as **Chiki**, a tiny pixelated chick running around a grassy arena while being chased by a long, wriggly snake.

Your goals:

- Collect **berries**, **mushrooms**, and **golden eggs**
- Use **power-ups** to survive longer
- Avoid **lava**, **water**, and of course the **snake**
- Reach the **portal** once you have enough score to complete the level
- Climb levels and set a **high score** (stored in a local SQLite database)

---

## ✨ Features

- Smooth tile-based movement with animations
- Smart snake AI using pathfinding (BFS)
- Multiple hazards:
  - 💧 Water – slows you
  - 🔥 Lava – damages you
- Power-ups:
  - 🍓 Berry – +1 score
  - 🍄 Mushroom – slows the snake
  - 🥚 Golden Egg – +1 life
  - 💨 Speed Boost – faster movement
  - 🛡️ Invincibility – temporary immunity
  - ❓ Confusion – reverses your controls and slows snake
  - ❄️ Freeze – stops the snake temporarily
- Pixel hearts for lives ❤️
- Level progression with increasing difficulty
- **Leaderboard** stored in a local `game_scores.db` (SQLite)
- Retro-style **HTML menu screen** built with CSS + Google Fonts
- Start game from browser → opens Pygame window

---

## 🧩 Tech Stack

- **Python**
  - `pygame`
  - `sqlite3`
  - `math`, `random`, `collections.deque`
- **Flask**
  - Serves the HTML menu
  - Provides a `/start_game` endpoint to launch the game
- **HTML/CSS**
  - Retro-styled menu (`templates/index.html`)

---

## 🛠️ Setup & Installation

### 1. Clone the repo

```bash
git clone https://github.com/Soumya2006nath/chikis-chase.git
cd chikis-chase
