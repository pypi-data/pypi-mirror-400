# TUI Wordle

Beautiful terminal-based Wordle game with shared leaderboard and streaks.

```
╦ ╦╔═╗╦═╗╔╦╗╦  ╔═╗
║║║║ ║╠╦╝ ║║║  ║╣
╚╩╝╚═╝╩╚══╩╝╩═╝╚═╝
```

## Features

- Daily Wordle with unique words each day
- Google login (one-click browser auth)
- Shared leaderboard with daily rankings
- Personal statistics & streaks
- GitHub-style contribution graph
- Auto-save (resume your game anytime)
- Beautiful TUI with animations
- Works offline too!

## Installation

```bash
# pip
pip install tui-wordle

# uv (Recommended)
uv tool install tui-wordle

# pipx
pipx install tui-wordle
```

## Play

```bash
wordle
```

## Controls

| Key | Action |
|-----|--------|
| A-Z | Type letter |
| Enter | Submit guess |
| Backspace | Delete letter |
| ESC | Quit |
| F1 | Statistics |
| F2 | Leaderboard |
| F3 | Help |
| F4 | Settings |

## License

MIT

## Credits

- Built with [Textual](https://textual.textualize.io/)
- Inspired by [Wordle](https://www.nytimes.com/games/wordle/)
