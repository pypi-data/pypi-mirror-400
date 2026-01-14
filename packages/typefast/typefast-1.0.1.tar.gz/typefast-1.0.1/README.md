# TypeFast

[![PyPI version](https://badge.fury.io/py/typefast.svg)](https://pypi.org/project/typefast/)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Terminal-based adaptive typing practice with progressive key learning and intelligent difficulty adjustment.

## ✨ Features

- 🎯 **Adaptive Learning** - Progressively unlocks keys as you master them
- 📊 **Real-time Analytics** - Track WPM, accuracy, and performance trends
- 🔄 **Intelligent Targeting** - Focuses practice on your weakest keys
- 📈 **Progress Visualization** - Beautiful ASCII charts showing improvement over time
- ⌨️ **Keybr-Style Error Handling** - Must type correct key to advance, wrong keys highlighted in red
- 🎨 **Clean Terminal UI** - Minimal, distraction-free interface
- 💾 **Persistent Stats** - Your progress is saved between sessions
- 🏆 **Performance Tracking** - View top speed, consistency scores, and detailed per-key analysis

## 🚀 Quick Start

### Installation

```bash
pip install typefast
```

### Run

```bash
typefast
```

That's it! Start typing and improve your skills.

## 📖 How It Works

TypeFast uses an adaptive learning system that:

1. **Starts Simple** - Begin with just the home row keys (a, s, d, f, j, k, l)
2. **Tracks Performance** - Monitors your speed and accuracy for each key
3. **Unlocks Progressively** - Adds new keys when you've mastered current ones
4. **Targets Weaknesses** - Generates exercises focusing on your difficult keys
5. **Shows Progress** - Visualizes your improvement over time with charts and statistics

## 🎮 Usage

### Basic Controls

- **Type** - Just start typing the displayed text
- **Backspace** - Skip current exercise and start a new one
- **Cmd+/Cmd-** - Increase/decrease font size
- **Ctrl+C** - Quit and save progress
- **Resize Terminal** - Drag terminal bigger to see extended statistics

### Understanding the Interface

```
TypeFast - Adaptive Typing Practice
WPM: 87 | Accuracy: 92% | Keys: 325 | Errors: 12

some hand fast first fast them play go first fast

Last 5: 118wpm | 93wpm | 81wpm | 89wpm | 94wpm
Avg: 88wpm | Top: 120wpm | Consistency: 83%

Key Difficulty (practice needed):
't': ████████████████░░░░ 39.5 (acc: 86.5%)
'y': ████████████░░░░░░░░ 33.6 (acc: 88.9%)
...

Per-Key Speed Analysis:
Fastest: u:117wpm | e:108wpm | n:101wpm
Slowest: g:65wpm | y:62wpm | t:59wpm

WPM Progress - All Time (325 rounds):
[Beautiful ASCII line chart showing your progress]
```

### Color Coding

- 🟢 **Green** - Correctly typed characters
- 🔴 **Red** - Characters where you made mistakes
- **White/Highlighted** - Current character to type
- **Gray** - Not yet typed

## 📊 Statistics Explained

### Main Stats
- **WPM** - Words per minute (5 characters = 1 word)
- **Accuracy** - Percentage of keystrokes without errors
- **Top Speed** - Your personal best WPM
- **Consistency** - How stable your performance is (lower variance = higher score)

### Advanced Stats (Tall Terminal)
- **Per-Key Speed** - Individual WPM for each key
- **Session Stats** - Current session accuracy and key count
- **Progress Chart** - All-time WPM trend across all sessions

## 🎯 Tips for Improvement

1. **Don't Look at Keyboard** - Force yourself to use touch typing
2. **Accuracy First** - Speed comes naturally with accuracy
3. **Practice Weak Keys** - TypeFast automatically targets these
4. **Regular Sessions** - 10-15 minutes daily beats marathon sessions
5. **Proper Posture** - Sit correctly and position hands on home row
6. **Use All Fingers** - Don't hunt-and-peck with index fingers

## 🛠️ Advanced Usage

### File Locations

TypeFast stores data in your home directory:

```
~/.typefast_stats.json       # Key statistics and progress
~/.typefast_history.json     # Historical WPM data
```

### Reset Progress

To start fresh:

```bash
rm ~/.typefast_stats.json ~/.typefast_history.json
```

### Customize Terminal

For best experience:
- **Font Size**: Use Cmd+/- to adjust
- **Window Size**: Drag larger to see more stats
- **Color Scheme**: Use a dark terminal theme

## 🤝 Contributing

Contributions welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

Inspired by [keybr.com](https://www.keybr.com/) and other typing practice tools.

## 📧 Contact

- GitHub: [@seikixtc](https://github.com/seikixtc)
- Issues: [GitHub Issues](https://github.com/seikixtc/typefast/issues)

## 🌟 Star History

If you find TypeFast useful, please consider giving it a star on GitHub!

---

**Happy Typing!** 🎹
