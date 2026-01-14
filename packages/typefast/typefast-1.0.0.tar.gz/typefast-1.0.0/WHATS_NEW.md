# TypeFast - Word-Based System

## What Makes TypeFast Different

TypeFast uses **real English words** with **intelligent targeting** to help you improve typing accuracy and speed efficiently.

## How It Works

### Always Real Words
Unlike many typing tutors that use random characters or nonsense syllables, TypeFast uses actual English vocabulary from the start.

### Example Practice Text

**Early Stage (Low Accuracy)**
```
sad fall ask all lads Dallas adds
```
Words seem random because they're specifically chosen to contain your weakest keys multiple times.

**Middle Stage (Improving)**
```
these hand after stand think left for
```
Mix of targeted practice and more natural flow.

**Advanced Stage (High Accuracy)**
```
the great hand will stand after these
```
Natural, sentence-like text with occasional difficult key practice.

## The Intelligence Behind It

### Difficulty Analysis
The system continuously tracks which keys you struggle with:
- Per-key accuracy (how often you type it correctly)
- Per-key speed (how fast you type it)
- Combined difficulty score (0-100)

### Word Selection Strategy

**Early Stage (<75% accuracy)**
- 90% of words must contain 2+ difficult keys
- Words appear random but are laser-focused on weak spots
- Example: If you struggle with 's', 'l', 'f' → picks words like "falls", "self", "false"

**Middle Stage (75-90% accuracy)**  
- 60% targeting difficult keys
- Beginning to form more natural sequences
- Balance between practice and readability

**Advanced Stage (>90% accuracy)**
- 30% targeting, mostly natural
- Starts sentences with articles ("the", "a", "this")
- Reads like normal English with occasional difficult words mixed in

## Why This Approach Works

### 1. Immediate Relevance
Every word you type is a real word you might use. No wasted practice on nonsense.

### 2. Efficient Learning
The system knows exactly which keys need work and selects words to maximize practice on those keys.

### 3. Natural Progression
As you improve, the text naturally becomes more sentence-like, keeping you engaged.

### 4. Builds Real Skills
You're not just learning key positions - you're learning to type actual English vocabulary at speed.

## Configuration

You can customize the word targeting system:

### Change Word Count
```python
self.current_text = self.generator.generate_text(word_count=8)  # Default
self.current_text = self.generator.generate_text(word_count=5)  # Shorter
self.current_text = self.generator.generate_text(word_count=15) # Longer
```

### Adjust Difficulty Targeting
```python
# In generate_text() method
if avg_accuracy < 75:
    difficulty_focus = 0.9  # Change to 0.7 for less aggressive targeting
    min_difficult_keys_per_word = 2  # Change to 1 for easier practice
```

### Add Custom Vocabulary
```python
# In TextGenerator.__init__()
self.real_words = [
    # Add your own words here
    'code', 'function', 'debug', 'compile'
]
```

## Backward Compatibility

Old stats files will work! The system automatically:
- Adds space to unlocked keys if missing
- Works with any existing key set
- Maintains all your progress

## Questions?

**Q: Why do the words seem random?**
A: They're not random - they're specifically chosen real English words that contain the letters you need to practice most. As you improve, word selection becomes more natural.

**Q: When will I see sentence-like text?**
A: Once your average accuracy reaches 90%, the app focuses less on difficult key targeting and creates more natural, sentence-like sequences.

**Q: Why doesn't space show in the difficulty chart?**
A: Space is treated differently since it's typed so frequently. The chart focuses on letter keys that need specific practice.

**Q: Will this work with Dvorak/Colemak?**
A: Yes! Just change the unlock order in `get_next_key_to_unlock()`.

## Summary

TypeFast provides intelligent typing practice that:
- ✅ Uses only real English words (no nonsense or random characters)
- ✅ Intelligently targets your weakest keys through word selection
- ✅ Adapts word selection based on your skill level
- ✅ Progresses from targeted practice to natural sentences
- ✅ Builds practical, real-world typing skills

Enjoy your improved typing practice! 🎹✨
