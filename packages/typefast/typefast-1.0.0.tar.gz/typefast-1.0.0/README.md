# TypeFast - Terminal-Based Adaptive Typing Practice

A CLI typing practice application with adaptive learning that tracks your progress and focuses on the keys you need to practice most.

## Features

### Core Features
- **Adaptive Key Learning**: Starts with home row keys and progressively unlocks new keys as you master current ones
- **Real Word Practice**: Always uses actual English words, never random characters or nonsense
- **Intelligent Targeting**: Continuously analyzes your typing to find keys you struggle with and selects words containing those letters
- **Progressive Text Quality**: Starts with words heavily targeting your weak keys (seems random), transitions to natural sentence-like text as you improve
- **Real-time Statistics**: Tracks WPM (words per minute) and accuracy
- **Per-Key Analytics**: Monitors accuracy and speed for each individual key
- **Difficulty Scoring**: Automatically identifies which keys need more practice
- **Persistent Progress**: Saves your statistics between sessions
- **Smart Key Unlocking**: Unlocks new keys when you've mastered current ones

### Additional Features
- Clean terminal UI with color-coded feedback
- Real-time visual difficulty bars for each key
- Session tracking across multiple practice sessions
- Natural text generation using common bigrams
- Immediate visual feedback (green = correct, red = error)

## Installation

### Requirements
- Python 3.6 or higher
- Unix-like terminal (Linux, macOS, WSL on Windows)

### Quick Install

**One-line installer** (after setting up on GitHub):
```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/typefast/main/install.sh | bash
```

**Manual install**:
1. Download the script:
```bash
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/typefast/main/typefast.py
chmod +x typefast.py
```

Or simply copy the `typefast.py` file to your system.

2. Run it:
```bash
python3 typefast.py
```

### Optional: Install Globally

To make it accessible from anywhere:

```bash
# Copy to local bin
sudo cp typefast.py /usr/local/bin/typefast
sudo chmod +x /usr/local/bin/typefast

# Now you can run it from anywhere
typefast
```

## Usage

### Starting the App

```bash
python3 typefast.py
```

Or if installed globally:
```bash
typefast
```

### How to Practice

1. **Type the displayed text**: The current character to type is highlighted with a yellow background
2. **Color feedback**:
   - Green = correctly typed
   - Red = error
   - Dim gray = not yet typed
   - Yellow highlight = current character

3. **Controls**:
   - Type normally to practice
   - Press `Backspace` to restart current exercise
   - Press `Ctrl+C` to quit and save progress

### Understanding the Interface

```
TypeFast - Adaptive Typing Practice
WPM: 45 | Accuracy: 97% | Keys: 156 | Errors: 5
Unlocked keys: [space]adfjkls
────────────────────────────────────────────────

              sad all ask fall lads

Key Difficulty (practice needed):
  's': ████████████████░░░░  82.3 (acc: 85.2%)
  'l': ████████████░░░░░░░░  65.1 (acc: 89.5%)
  'f': ██████░░░░░░░░░░░░░░  32.4 (acc: 95.1%)
```

- **WPM**: Your current words per minute
- **Accuracy**: Percentage of correct keystrokes
- **Keys**: Total keys typed this session
- **Errors**: Total errors this session
- **Unlocked keys**: All keys currently available for practice
- **Key Difficulty**: Shows which keys need the most practice (higher = needs more work)

### Progressive Learning System

The app uses an intelligent progressive system with real word practice:

1. **Start with home row**: You begin with `asdf jkl` and space
2. **Practice with targeted words**: Type real English words that heavily feature your weakest keys
3. **Master current keys**: Practice until your accuracy improves (>75%)
4. **Unlock new keys**: When you've mastered current keys, new keys unlock automatically
5. **Transition to natural text**: As your accuracy increases (>90%), word selection becomes more natural and sentence-like
6. **Expand your vocabulary**: Keys unlock in order of frequency in English

The word selection is intelligent:
- **Below 75% accuracy**: 90% of words contain multiple difficult keys (appears random but targets weak spots)
- **75-90% accuracy**: 60% targeting, beginning to form more natural sequences  
- **Above 90% accuracy**: 30% targeting, mostly natural sentence-like text

### Tips for Effective Practice

1. **Focus on accuracy first**: Speed will come naturally with accuracy
2. **Watch the difficulty bars**: They show which keys need more attention
3. **Practice regularly**: Short, frequent sessions are more effective than long ones
4. **Don't look at the keyboard**: Force yourself to learn by feel
5. **Maintain good posture**: Proper ergonomics prevent fatigue

## Data Storage

Your progress is saved in `~/.typefast_stats.json` and includes:
- Per-key accuracy statistics
- Per-key speed measurements
- Total keys typed
- Session count
- Unlocked keys

You can reset your progress by deleting this file:
```bash
rm ~/.typefast_stats.json
```

## How the Adaptive Learning Works

### Difficulty Scoring
Each key gets a difficulty score (0-100) based on:
- **Accuracy (70% weight)**: How often you type it correctly
- **Speed (30% weight)**: How fast you type it compared to average

### Key Unlocking Algorithm
New keys unlock when:
1. Average difficulty of current keys < 20%
2. You've typed at least 50 keys per unlocked key (sufficient practice)

### Practice Text Generation
The generator creates text using real English words that:
- Heavily feature your weakest keys early on (words appear random but are specifically chosen)
- Gradually transitions to more natural word sequences as you improve
- At high accuracy, creates sentence-like text with occasional difficult key practice
- Always uses actual English vocabulary - no nonsense words

## Technical Details

- **Language**: Python 3
- **UI Library**: curses (built-in)
- **Storage**: JSON file in home directory
- **Statistics**: Rolling window of last 50 keystrokes per key
- **Performance**: Updates at 10 FPS (100ms refresh)

## Customization

You can modify the script to customize:

- **Starting keys**: Change `self.unlocked_keys` in `TypingStats.__init__`
- **Unlock threshold**: Modify the difficulty threshold in `should_unlock_new_key()`
- **Text length**: Adjust `length` parameter in `generate_text()`
- **Key unlock order**: Edit `unlock_order` in `get_next_key_to_unlock()`
- **Colors**: Modify `curses.init_pair()` calls in the `run()` method

## Troubleshooting

### Issue: Colors not showing
Some terminals don't support colors. Try a modern terminal like iTerm2, Alacritty, or Terminal.app.

### Issue: Keys not registering
Make sure your terminal window is focused and you're not in a screen/tmux session that's capturing keys.

### Issue: Display looks wrong
Resize your terminal to at least 80x24 characters for best results.

### Issue: Permission denied
Make sure the script is executable:
```bash
chmod +x typefast.py
```

## Contributing

This is a single-file Python script, making it easy to modify. Feel free to:
- Add new features
- Improve the text generation algorithm
- Add word-based practice modes
- Implement lessons or structured courses
- Add support for special characters and numbers

## License

MIT License - feel free to use, modify, and distribute.

---

Happy typing! 🎹✨
