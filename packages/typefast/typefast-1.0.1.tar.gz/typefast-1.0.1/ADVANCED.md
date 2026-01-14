# TypeFast - Advanced Configuration

## Customization Options

TypeFast is a single Python file, making it easy to customize. Here are the main configuration options you can modify.

## 1. Starting Keys

**Location**: `TypingStats.__init__()` method, line ~37

```python
# Default: Home row + space
self.unlocked_keys = {'a', 's', 'd', 'f', 'j', 'k', 'l', ' '}

# Alternative: All letters immediately
self.unlocked_keys = set('abcdefghijklmnopqrstuvwxyz ')

# Alternative: Most common English letters
self.unlocked_keys = {'e', 't', 'a', 'o', 'i', 'n', 's', ' '}
```

## 2. Key Unlock Order

**Location**: `get_next_key_to_unlock()` method, line ~97

```python
unlock_order = [
    'a', 's', 'd', 'f', 'j', 'k', 'l', ' ',  # home row + space
    'g', 'h',  # inner keys
    'e', 'i', 'r', 't', 'n', 'o',  # most common letters
    'u', 'w', 'y', 'p', 'c', 'm',  # common letters
    'b', 'v', 'q', 'x', 'z',  # less common
]

# Example: Dvorak layout
unlock_order = [
    'a', 'o', 'e', 'u', 'h', 't', 'n', 's', ' ',  # Dvorak home row
    # ... rest of dvorak
]

# Example: Frequency-first approach
unlock_order = [
    'e', 't', 'a', 'o', 'i', 'n', ' ',  # highest frequency
    's', 'h', 'r', 'd', 'l',
    # ... rest by frequency
]
```

## 3. Unlock Threshold

**Location**: `should_unlock_new_key()` method, line ~88

```python
# Default: Unlock when avg difficulty < 20
return avg_difficulty < 20 and self.total_keys > len(self.unlocked_keys) * 50

# More aggressive: Unlock faster
return avg_difficulty < 30 and self.total_keys > len(self.unlocked_keys) * 30

# More conservative: Require mastery
return avg_difficulty < 10 and self.total_keys > len(self.unlocked_keys) * 100
```

## 7. Color Scheme

**Location**: `get_difficulty_score()` method, line ~69

```python
# Default: 70% accuracy weight, 30% speed weight
difficulty = (accuracy_score * 0.7) + (speed_score * 0.3)

# Emphasize speed more
difficulty = (accuracy_score * 0.5) + (speed_score * 0.5)

# Emphasize accuracy only
difficulty = accuracy_score
```

## 5. Difficulty Targeting Intensity

**Location**: `generate_text()` method, line ~255

```python
# Default: Adaptive targeting based on accuracy
if avg_accuracy < 75:
    difficulty_focus = 0.9  # 90% words contain difficult keys
    min_difficult_keys_per_word = 2
elif avg_accuracy < 90:
    difficulty_focus = 0.6  # 60% targeting
    min_difficult_keys_per_word = 1
else:
    difficulty_focus = 0.3  # 30% targeting

# More aggressive targeting (harder practice)
if avg_accuracy < 75:
    difficulty_focus = 1.0
    min_difficult_keys_per_word = 3
elif avg_accuracy < 90:
    difficulty_focus = 0.8
    min_difficult_keys_per_word = 2
else:
    difficulty_focus = 0.5

# More relaxed targeting (easier, more natural)
if avg_accuracy < 75:
    difficulty_focus = 0.7
    min_difficult_keys_per_word = 1
elif avg_accuracy < 90:
    difficulty_focus = 0.4
    min_difficult_keys_per_word = 1
else:
    difficulty_focus = 0.1
```

## 6. Number of Words Per Exercise

**Location**: `start_new_text()` method, line ~223

```python
# Default: 8 words
self.current_text = self.generator.generate_text(word_count=8)

# Shorter exercises
self.current_text = self.generator.generate_text(word_count=5)

# Longer exercises
self.current_text = self.generator.generate_text(word_count=15)
```

**Location**: `run()` method, line ~316

```python
# Default colors
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Correct
curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # Error
curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Current

# Alternative: Blue theme
curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)

# High contrast
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
```

## 8. Statistics Storage Location

**Location**: `TypingStats.__init__()`, line ~24

```python
# Default: Home directory
def __init__(self, stats_file='~/.typefast_stats.json'):

# Alternative: XDG config
def __init__(self, stats_file='~/.config/typefast/stats.json'):

# Alternative: Current directory
def __init__(self, stats_file='./typefast_stats.json'):
```

## 9. Key Speed Window

**Location**: `record_keystroke()` method, line ~55

```python
# Default: Keep last 50 timings
if len(self.key_speed[key]) > 50:
    self.key_speed[key] = self.key_speed[key][-50:]

# Smaller window (faster adaptation)
if len(self.key_speed[key]) > 20:
    self.key_speed[key] = self.key_speed[key][-20:]

# Larger window (more stable stats)
if len(self.key_speed[key]) > 100:
    self.key_speed[key] = self.key_speed[key][-100:]
```

## 10. UI Refresh Rate

**Location**: `run()` method, line ~318

```python
# Default: 100ms (10 FPS)
stdscr.timeout(100)

# Faster updates (20 FPS)
stdscr.timeout(50)

# Slower updates (save CPU, 5 FPS)
stdscr.timeout(200)
```

## Advanced Feature Ideas

### Customize Word List

Add your own vocabulary by modifying `self.real_words` in `TextGenerator.__init__()`:

```python
# Domain-specific vocabulary
self.real_words = [
    # Programming terms
    'code', 'function', 'variable', 'class', 'method', 'array',
    'string', 'loop', 'if', 'else', 'return', 'import', 'def',
    # ... add more
]

# Medical vocabulary
self.real_words = [
    'patient', 'diagnosis', 'treatment', 'symptom', 'medicine',
    # ... add more
]

# Your own practice text
self.real_words = [
    # Words from your job, hobby, etc.
]
```

### Add Word Mode

Add after line ~223:

```python
def generate_word_text(self, word_count=10):
    """Generate actual English words"""
    common_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her']
    # Filter by unlocked keys
    available_words = [w for w in common_words 
                      if all(c in self.stats.unlocked_keys for c in w)]
    return ' '.join(random.choices(available_words, k=word_count))
```

### Add Numbers and Symbols

Add to unlock order:

```python
unlock_order = [
    # Letters first...
    'a', 's', 'd', 'f', 'j', 'k', 'l', ';',
    # Then numbers
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
    # Then symbols
    '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
]
```

### Add Lessons/Levels

```python
LESSONS = {
    1: {'keys': 'asdf', 'target_wpm': 20},
    2: {'keys': 'asdfgh', 'target_wpm': 25},
    3: {'keys': 'asdfghjkl', 'target_wpm': 30},
    # etc...
}
```

### Add Typing Game Mode

```python
def generate_falling_text(self):
    """Generate text that 'falls' down the screen"""
    # Implementation for a game mode
    pass
```

### Add Statistics Dashboard

```python
def show_stats_screen(self):
    """Show detailed statistics and graphs"""
    # WPM over time
    # Accuracy trends
    # Time practiced
    # Best/worst keys
    pass
```

## Example: Complete Custom Configuration

Here's a complete example for a programmer-focused configuration:

```python
# In __init__:
self.unlocked_keys = {'a', 's', 'd', 'f', 'j', 'k', 'l', ';'}

# In get_next_key_to_unlock:
unlock_order = [
    'a', 's', 'd', 'f', 'j', 'k', 'l', ';',  # home row
    'g', 'h',  # inner
    '{', '}', '(', ')', '[', ']',  # brackets first
    '=', '-', '+', '_',  # operators
    'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',  # top row
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',  # numbers
    'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.',  # bottom
]

# More aggressive unlocking
# In should_unlock_new_key:
return avg_difficulty < 30 and self.total_keys > len(self.unlocked_keys) * 30
```

## Tips for Customization

1. **Test your changes**: Run `python3 typefast.py` after each modification
2. **Keep a backup**: Copy the original file first
3. **Start small**: Change one thing at a time
4. **Consider your goals**: Different configurations suit different learning styles

## Need Help?

If you create an interesting configuration, consider sharing it! The modular design makes it easy to swap configurations.
