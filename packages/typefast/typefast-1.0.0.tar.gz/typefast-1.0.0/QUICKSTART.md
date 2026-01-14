# TypeFast - Quick Start Guide

## Installation (30 seconds)

```bash
# Download or copy typefast.py to your computer

# Make it executable
chmod +x typefast.py

# Run it!
python3 typefast.py
```

## First Time Using It

When you first start TypeFast:

1. You'll see 8 keys available: `asdf jkl` and space (home row)
2. Practice text with real English words will appear, heavily featuring your weakest keys
3. Start typing! The current character is highlighted in yellow
4. Green = correct, Red = wrong
5. When you finish the text, a new one appears automatically

The words might seem random at first (like "sad all fall ask"), but they're specifically chosen to target the keys you need to practice most. As you improve, the text becomes more natural and sentence-like.

## Understanding the Stats

```
WPM: 45 | Accuracy: 97% | Keys: 156 | Errors: 5
```

- **WPM**: Words per minute (chars ÷ 5 ÷ minutes)
- **Accuracy**: % of keys typed correctly
- **Keys**: Total keys you've typed this session
- **Errors**: How many mistakes you've made

## The Key Difficulty Chart

```
Key Difficulty (practice needed):
  's': ████████████████░░░░  82.3 (acc: 85.2%)
  'l': ████████████░░░░░░░░  65.1 (acc: 89.5%)
  'f': ██████░░░░░░░░░░░░░░  32.4 (acc: 95.1%)
```

- Bars show how much each key needs practice
- Higher difficulty = needs more work
- The app will focus practice on these keys

## How Keys Unlock

1. **Start**: 8 home row keys + space
2. **Practice**: Type words until you master them (>80% accuracy, decent speed)
3. **Unlock**: New key appears automatically!
4. **Progress**: Keep going until you've unlocked all letters

The order is smart - based on letter frequency:
- Home row first: `asdf jkl` + space
- Then inner: `gh`
- Most common: `eirtno`
- Then the rest in order of frequency

## Tips for Fast Progress

### 1. Accuracy > Speed
Don't rush! Type slowly and correctly. Speed comes naturally.

### 2. Don't Look Down
Force yourself to learn by feel, not sight.

### 3. Short Sessions
Practice 10-15 minutes daily > 1 hour weekly

### 4. Watch the Difficulty Bars
Focus on your weakest keys during practice.

### 5. Proper Posture
- Fingers on home row
- Elbows at 90°
- Screen at eye level

## Controls

- **Type normally**: Practice!
- **Backspace**: Skip to new text
- **Ctrl+C**: Quit (saves automatically)

## Your Progress is Saved

Everything saves to `~/.typefast_stats.json`:
- Which keys you've unlocked
- Accuracy for each key
- Speed for each key
- Total practice time

Come back anytime and pick up where you left off!

## Common Questions

**Q: Why do the words seem random?**
A: They are real English words, but they're specifically chosen to feature the keys you struggle with most. As your accuracy improves (>90%), the word selection becomes more natural and sentence-like.

**Q: Why am I still on home row?**
A: You need >80% accuracy on current keys. Keep practicing!

**Q: Can I skip keys?**
A: No, the progression is designed to build proper technique.

**Q: What's a good WPM?**
A: 
- Beginner: 20-30 WPM
- Average: 40-50 WPM
- Good: 60-70 WPM
- Excellent: 80+ WPM

**Q: How long to learn touch typing?**
A: With daily practice:
- Basic proficiency: 2-4 weeks
- All keys unlocked: 4-6 weeks
- High speed: 2-3 months

**Q: It's too easy/hard!**
A: The app adapts! If it's easy, you'll unlock keys faster.

## Troubleshooting

**Terminal too small**: Resize to at least 80x24 characters

**Keys not working**: Make sure terminal is focused

**Colors not showing**: Use a modern terminal (iTerm2, Alacritty, etc.)

**Want to reset**: Delete `~/.typefast_stats.json`

## Ready to Type?

```bash
python3 typefast.py
```

Good luck! 🎹✨

---

*Remember: Touch typing is a skill like any other. Consistent practice beats intensity. 15 minutes daily will get you there!*
