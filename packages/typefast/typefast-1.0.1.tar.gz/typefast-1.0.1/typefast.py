#!/usr/bin/env python3
"""
TypeFast - Terminal-based Adaptive Typing Practice
Progressive key learning system for efficient typing skill development
"""

import curses
import time
import json
import os
import random
import string
from collections import defaultdict
from pathlib import Path
import math

class TypingStats:
    """Track typing statistics and adaptive learning"""
    
    def __init__(self, stats_file='~/.typefast_stats.json'):
        self.stats_file = Path(stats_file).expanduser()
        self.load_stats()
        
    def load_stats(self):
        """Load statistics from file"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                data = json.load(f)
                self.key_accuracy = defaultdict(lambda: {'correct': 0, 'incorrect': 0}, data.get('key_accuracy', {}))
                self.key_speed = defaultdict(list, data.get('key_speed', {}))
                self.total_keys = data.get('total_keys', 0)
                self.session_count = data.get('session_count', 0)
                self.unlocked_keys = set(data.get('unlocked_keys', ['a', 's', 'd', 'f', 'j', 'k', 'l', ' ']))
        else:
            self.key_accuracy = defaultdict(lambda: {'correct': 0, 'incorrect': 0})
            self.key_speed = defaultdict(list)
            self.total_keys = 0
            self.session_count = 0
            # Start with home row keys + space
            self.unlocked_keys = {'a', 's', 'd', 'f', 'j', 'k', 'l', ' '}
    
    def save_stats(self):
        """Save statistics to file"""
        data = {
            'key_accuracy': dict(self.key_accuracy),
            'key_speed': dict(self.key_speed),
            'total_keys': self.total_keys,
            'session_count': self.session_count,
            'unlocked_keys': list(self.unlocked_keys)
        }
        with open(self.stats_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_keystroke(self, key, correct, time_ms):
        """Record a keystroke"""
        if correct:
            self.key_accuracy[key]['correct'] += 1
        else:
            self.key_accuracy[key]['incorrect'] += 1
        
        self.key_speed[key].append(time_ms)
        # Keep only last 50 timings per key
        if len(self.key_speed[key]) > 50:
            self.key_speed[key] = self.key_speed[key][-50:]
        
        self.total_keys += 1
    
    def get_accuracy(self, key):
        """Get accuracy percentage for a key"""
        stats = self.key_accuracy[key]
        total = stats['correct'] + stats['incorrect']
        if total == 0:
            return 100.0
        return (stats['correct'] / total) * 100
    
    def get_avg_speed(self, key):
        """Get average speed (ms) for a key"""
        speeds = self.key_speed[key]
        if not speeds:
            return 0
        return sum(speeds) / len(speeds)
    
    def get_difficulty_score(self, key):
        """Calculate difficulty score (0-100, higher = needs more practice)"""
        if key not in self.unlocked_keys:
            return 0
        
        accuracy = self.get_accuracy(key)
        avg_speed = self.get_avg_speed(key)
        
        # Normalize speed (assume 200ms is average, 100ms is excellent)
        speed_score = min(100, (avg_speed / 200) * 50) if avg_speed > 0 else 50
        accuracy_score = 100 - accuracy
        
        # Weight accuracy more heavily
        difficulty = (accuracy_score * 0.7) + (speed_score * 0.3)
        return difficulty
    
    def should_unlock_new_key(self):
        """Determine if user is ready for a new key"""
        if len(self.unlocked_keys) >= 26:  # All letters unlocked
            return False
        
        # Check if current keys are mastered
        difficulties = [self.get_difficulty_score(k) for k in self.unlocked_keys if k.isalpha()]
        avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else 100
        
        # Get number of letter keys (not counting space)
        num_letter_keys = len([k for k in self.unlocked_keys if k.isalpha()])
        
        # Early stage (first 10 keys): Easier unlock requirements to progress faster
        if num_letter_keys <= 10:
            # Unlock when avg difficulty < 30 and practiced at least 30 keys per letter
            return avg_difficulty < 30 and self.total_keys > num_letter_keys * 30
        else:
            # Later stage: Standard requirements
            # Unlock new key when average difficulty is low and sufficient practice
            return avg_difficulty < 20 and self.total_keys > len(self.unlocked_keys) * 50
    
    def get_next_key_to_unlock(self):
        """Get the next key to unlock based on home row progression"""
        # Progressive key unlock order (expanding from home row)
        unlock_order = [
            'a', 's', 'd', 'f', 'j', 'k', 'l', ' ',  # home row + space
            'g', 'h',  # inner keys
            'e', 'i', 'r', 't', 'n', 'o',  # most common letters
            'u', 'w', 'y', 'p', 'c', 'm',  # common letters
            'b', 'v', 'q', 'x', 'z',  # less common
        ]
        
        for key in unlock_order:
            if key not in self.unlocked_keys:
                return key
        return None

class TextGenerator:
    """Generate practice text based on difficulty profile using words"""
    
    def __init__(self, stats):
        self.stats = stats
        
        # English syllable patterns for pronounceable words
        self.consonants = 'bcdfghjklmnpqrstvwxyz'
        self.vowels = 'aeiou'
        
        # Common word patterns (C=consonant, V=vowel)
        self.syllable_patterns = [
            'CV', 'CVC', 'VC', 'CCV', 'VCC', 'CVCC', 'CCVC'
        ]
        
        # Common English words by frequency (most common first)
        self.real_words = [
            # 100 most common English words
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'it',
            'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this',
            'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or',
            'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so',
            'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when',
            'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take', 'people',
            'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than',
            'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back',
            'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even',
            'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us', 'is',
            # Additional common words
            'was', 'are', 'been', 'has', 'had', 'were', 'said', 'did', 'may', 'must',
            'such', 'here', 'where', 'why', 'find', 'long', 'down', 'call', 'own', 'old',
            'right', 'left', 'high', 'low', 'fast', 'slow', 'big', 'small', 'great', 'best',
            'man', 'woman', 'child', 'world', 'life', 'hand', 'part', 'place', 'case', 'point',
            'ask', 'seem', 'feel', 'try', 'leave', 'hand', 'keep', 'let', 'begin', 'help',
            'show', 'hear', 'play', 'run', 'move', 'live', 'believe', 'bring', 'happen', 'write',
            'sit', 'stand', 'lose', 'pay', 'meet', 'include', 'continue', 'set', 'learn', 'change',
            'lead', 'understand', 'watch', 'follow', 'stop', 'create', 'speak', 'read', 'allow', 'add'
        ]
        
        # Common bigrams and trigrams for natural words
        self.common_bigrams = {
            'th', 'he', 'in', 'er', 'an', 're', 'on', 'at', 'en', 'nd',
            'ti', 'es', 'or', 'te', 'of', 'ed', 'is', 'it', 'al', 'ar',
            'st', 'to', 'nt', 'ng', 'se', 'ha', 'as', 'ou', 'io', 'le',
            'ea', 'ch', 'wh', 'sh', 'oo', 'ee', 'ai', 'ay', 'ly', 'el'
        }
        
        self.common_trigrams = {
            'the', 'and', 'ing', 'ion', 'tio', 'ent', 'ati', 'for', 'her', 'ter',
            'hat', 'tha', 'ere', 'ate', 'his', 'con', 'ver', 'all', 'ons', 'est'
        }
    
    def can_type_word(self, word):
        """Check if all letters in word are unlocked"""
        return all(c in self.stats.unlocked_keys for c in word.lower())
    
    def get_usable_real_words(self):
        """Get real words that can be typed with unlocked keys"""
        return [w for w in self.real_words if self.can_type_word(w)]
    
    def generate_pronounceable_word(self, min_len=3, max_len=7, target_keys=None):
        """Generate a pronounceable pseudo-word targeting specific keys"""
        unlocked = list(self.stats.unlocked_keys)
        if not unlocked:
            return "asdf"
        
        # Get available consonants and vowels
        available_consonants = [c for c in self.consonants if c in unlocked]
        available_vowels = [c for c in self.vowels if c in unlocked]
        
        if not available_consonants or not available_vowels:
            # Fallback to any available letters
            return ''.join(random.choices(unlocked, k=random.randint(min_len, max_len)))
        
        # Build word using syllable patterns
        word = []
        target_length = random.randint(min_len, max_len)
        
        # If we have target keys (difficult keys), try to include them
        if target_keys:
            # Start with a target key
            start_key = random.choice(target_keys)
            word.append(start_key)
            is_vowel = start_key in available_vowels
        else:
            # Start with consonant or vowel randomly
            is_vowel = random.random() < 0.3
            if is_vowel:
                word.append(random.choice(available_vowels))
            else:
                word.append(random.choice(available_consonants))
        
        # Build rest of word with alternating pattern
        while len(word) < target_length:
            if is_vowel:
                # Add consonant
                if target_keys:
                    # Try to use a difficult consonant
                    difficult_consonants = [c for c in target_keys if c in available_consonants]
                    if difficult_consonants and random.random() < 0.5:
                        word.append(random.choice(difficult_consonants))
                    else:
                        word.append(random.choice(available_consonants))
                else:
                    word.append(random.choice(available_consonants))
                is_vowel = False
            else:
                # Add vowel
                if target_keys:
                    difficult_vowels = [v for v in target_keys if v in available_vowels]
                    if difficult_vowels and random.random() < 0.5:
                        word.append(random.choice(difficult_vowels))
                    else:
                        word.append(random.choice(available_vowels))
                else:
                    word.append(random.choice(available_vowels))
                is_vowel = True
        
        return ''.join(word)
    
    def get_difficult_keys(self, count=3):
        """Get the most difficult keys that need practice"""
        key_difficulties = [(k, self.stats.get_difficulty_score(k)) 
                           for k in self.stats.unlocked_keys 
                           if k.isalpha()]  # Only letters, no punctuation
        key_difficulties.sort(key=lambda x: x[1], reverse=True)
        return [k for k, _ in key_difficulties[:count]]
    
    def generate_text(self, word_count=10):
        """Generate practice text with words targeting difficult keys"""
        real_words = self.get_usable_real_words()
        difficult_keys = self.get_difficult_keys(count=5)  # Get top 5 difficult keys
        
        if not real_words:
            # Fallback if no real words available with current keys
            return ' '.join([self.generate_pronounceable_word(3, 6) for _ in range(word_count)])
        
        # Determine how much to focus on difficult keys based on progress
        total_accuracy = sum(self.stats.get_accuracy(k) for k in self.stats.unlocked_keys if k.isalpha())
        avg_accuracy = total_accuracy / max(1, len([k for k in self.stats.unlocked_keys if k.isalpha()]))
        
        # Count available letter keys
        num_letter_keys = len([k for k in self.stats.unlocked_keys if k.isalpha()])
        
        # Calculate difficulty focus percentage
        # Very early stage (< 10 keys): Much lower focus to avoid too much repetition
        # Early (<75%): Heavily target difficult keys
        # Middle (75-90%): Moderate targeting
        # Late (>90%): Light targeting - mostly natural sentences
        if num_letter_keys < 10:
            # Special handling for very limited key sets
            difficulty_focus = 0.3  # 30% targeting (minimal to maximize variety)
            min_difficult_keys_per_word = 0  # Don't require difficult keys
        elif avg_accuracy < 75:
            difficulty_focus = 0.9  # 90% of words must contain difficult keys
            min_difficult_keys_per_word = 2  # Prefer words with multiple difficult keys
        elif avg_accuracy < 90:
            difficulty_focus = 0.6  # 60% focus on difficult keys
            min_difficult_keys_per_word = 1  # At least one difficult key per word
        else:
            difficulty_focus = 0.3  # 30% focus, mostly natural
            min_difficult_keys_per_word = 0  # Natural word choice
        
        # Categorize words by how many difficult keys they contain
        words_by_difficulty = {i: [] for i in range(6)}
        for word in real_words:
            difficult_count = sum(1 for k in difficult_keys if k in word)
            if difficult_count < 6:
                words_by_difficulty[difficult_count].append(word)
        
        words = []
        last_word = None  # Track last word to avoid repetition
        
        for _ in range(word_count):
            # Always filter out the last word to prevent consecutive repeats
            available_words = [w for w in real_words if w != last_word] if last_word else real_words
            
            if not available_words:
                available_words = real_words
            
            if difficult_keys and random.random() < difficulty_focus:
                # Pick word that contains difficult keys
                # Try to find words with minimum required difficult keys
                candidates = []
                for difficulty_level in range(5, min_difficult_keys_per_word - 1, -1):
                    if words_by_difficulty[difficulty_level]:
                        # Only add words that aren't the last word
                        level_candidates = [w for w in words_by_difficulty[difficulty_level] if w != last_word]
                        candidates.extend(level_candidates)
                        if difficulty_level >= min_difficult_keys_per_word and candidates:
                            break
                
                # Remove duplicates
                candidates = list(set(candidates))
                
                if candidates:
                    chosen_word = random.choice(candidates)
                else:
                    # Fallback to any available word
                    chosen_word = random.choice(available_words)
            else:
                # Natural word selection from available words
                chosen_word = random.choice(available_words)
            
            words.append(chosen_word)
            last_word = chosen_word
        
        # High accuracy: try to make more sentence-like by starting with articles/common starters
        if avg_accuracy > 90:
            sentence_starters = [w for w in real_words if w in ['the', 'a', 'this', 'that', 'these', 'those', 'my', 'your', 'our', 'some', 'many']]
            if sentence_starters and words:
                words[0] = random.choice(sentence_starters)
        
        return ' '.join(words)

class TypingApp:
    """Main typing practice application"""
    
    def __init__(self):
        self.stats = TypingStats()
        self.generator = TextGenerator(self.stats)
        self.current_text = ""
        self.typed_text = ""
        self.errors = 0
        self.start_time = None
        self.last_key_time = None
        self.session_keys = 0
        self.session_errors = 0
        self.last_wpm = 0
        self.last_accuracy = 100
        self.exercise_completed = False
        self.recent_wpms = []
        self.current_char_errors = 0  # Errors on current character
        self.error_positions = set()  # Positions where errors occurred
        self.load_history()
    
    def load_history(self):
        """Load WPM history from stats"""
        history_file = Path('~/.typefast_history.json').expanduser()
        if history_file.exists():
            with open(history_file, 'r') as f:
                data = json.load(f)
                self.wpm_history = data.get('wpm_history', [])
        else:
            self.wpm_history = []
    
    def save_history(self):
        """Save WPM history"""
        history_file = Path('~/.typefast_history.json').expanduser()
        with open(history_file, 'w') as f:
            json.dump({'wpm_history': self.wpm_history}, f)
    
    def start_new_text(self):
        """Start a new typing exercise"""
        if self.stats.should_unlock_new_key():
            new_key = self.stats.get_next_key_to_unlock()
            if new_key:
                self.stats.unlocked_keys.add(new_key)
                self.stats.save_stats()
        
        self.current_text = self.generator.generate_text(word_count=20)
        self.typed_text = ""
        self.errors = 0
        self.current_char_errors = 0
        self.error_positions = set()
        self.start_time = None
        self.last_key_time = None
        self.exercise_completed = False
    
    def process_key(self, key):
        """Process a typed key"""
        if not self.current_text:
            return
        
        # Start timer on first keystroke
        if self.start_time is None:
            self.start_time = time.time()
            self.last_key_time = self.start_time
        
        current_time = time.time()
        key_time_ms = (current_time - self.last_key_time) * 1000
        
        if len(self.typed_text) < len(self.current_text):
            expected = self.current_text[len(self.typed_text)]
            correct = (key == expected)
            
            if correct:
                # Only advance if correct key was pressed
                self.stats.record_keystroke(expected, True, key_time_ms)
                self.typed_text += key
                self.session_keys += 1
                self.last_key_time = current_time
                self.current_char_errors = 0  # Reset error count for next character
                
                # Check if text completed
                if len(self.typed_text) == len(self.current_text):
                    # Store final stats before resetting
                    self.last_wpm = self.get_wpm()
                    self.last_accuracy = self.get_accuracy()
                    self.exercise_completed = True
                    
                    # Add to recent WPMs (keep last 5)
                    self.recent_wpms.append(self.last_wpm)
                    if len(self.recent_wpms) > 5:
                        self.recent_wpms.pop(0)
                    
                    # Add to all-time history with timestamp
                    self.wpm_history.append({
                        'wpm': self.last_wpm,
                        'timestamp': time.time(),
                        'accuracy': self.last_accuracy
                    })
                    self.save_history()
                    
                    return True  # Text completed
            else:
                # Wrong key pressed - record error but don't advance
                self.errors += 1
                self.session_errors += 1
                self.current_char_errors += 1
                self.error_positions.add(len(self.typed_text))  # Mark this position
                self.stats.record_keystroke(expected, False, key_time_ms)
        
        return False
    
    def get_wpm(self):
        """Calculate words per minute"""
        if not self.start_time:
            return 0
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0
        chars = len(self.typed_text)
        wpm = (chars / 5) / (elapsed / 60)
        return int(wpm)
    
    def get_accuracy(self):
        """Calculate current accuracy"""
        if not self.typed_text:
            return 100
        correct = len(self.typed_text) - self.errors
        return int((correct / len(self.typed_text)) * 100)
    
    def draw_interface(self, stdscr):
        """Draw the typing interface"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Title
        title = "TypeFast - Adaptive Typing Practice"
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
        
        # Stats bar - use last completed stats if just finished
        if self.exercise_completed:
            wpm = self.last_wpm
            acc = self.last_accuracy
        else:
            wpm = self.get_wpm()
            acc = self.get_accuracy()
        
        stats_str = f"WPM: {wpm:3d} | Accuracy: {acc:3d}% | Keys: {self.session_keys} | Errors: {self.session_errors}"
        stdscr.addstr(1, (width - len(stats_str)) // 2, stats_str)
        
        # Unlocked keys
        unlocked_display = ''.join(sorted([k if k != ' ' else '[space]' for k in self.stats.unlocked_keys]))
        unlocked_str = f"Unlocked keys: {unlocked_display}"
        stdscr.addstr(2, 2, unlocked_str, curses.A_DIM)
        
        # Separator
        stdscr.addstr(3, 0, "─" * width)
        
        # Text display area (fixed position near top)
        text_start_row = 8  # Fixed position instead of centered
        
        if self.current_text:
            # Split text into two lines (roughly half)
            words = self.current_text.split()
            mid_point = len(words) // 2
            line1 = ' '.join(words[:mid_point])
            line2 = ' '.join(words[mid_point:])
            
            typed_len = len(self.typed_text)
            
            # Display line 1
            self._draw_text_line(stdscr, line1, 0, typed_len, text_start_row, width)
            
            # Display line 2
            self._draw_text_line(stdscr, line2, len(line1) + 1, typed_len, text_start_row + 1, width)
        
        # Draw scoreboard and stats
        self.draw_scoreboard(stdscr, text_start_row, height, width)
    
    def _draw_text_line(self, stdscr, line_text, line_start_pos, typed_len, row, width):
        """Helper to draw a single line of text with colors"""
        if not line_text:
            return
            
        text_start_col = (width - len(line_text)) // 2
        
        for i, char in enumerate(line_text):
            col = text_start_col + i
            if col >= width - 1:
                break
            
            global_pos = line_start_pos + i
            
            try:
                if global_pos < typed_len:
                    # Already typed
                    if global_pos in self.error_positions:
                        # This character had an error - show in red
                        stdscr.addstr(row, col, char, curses.color_pair(2))
                    else:
                        # Correct - show in green
                        stdscr.addstr(row, col, char, curses.color_pair(1))
                elif global_pos == typed_len:
                    # Current character (cursor) - just reverse video
                    stdscr.addstr(row, col, char, curses.A_REVERSE)
                else:
                    # Not yet typed
                    stdscr.addstr(row, col, char, curses.A_DIM)
            except curses.error:
                pass
    
    def draw_scoreboard(self, stdscr, text_start_row, height, width):
        """Draw scoreboard and statistics"""
        # Scoreboard (below text)
        scoreboard_row = text_start_row + 4  # Leave room for 2 lines of text
        if scoreboard_row < height - 15:  # Only show if there's room
            try:
                # Recent rounds in compact format
                if self.recent_wpms:
                    # Reverse to show most recent first
                    rounds_str = "Last 5: " + " | ".join([f"{wpm}wpm" for wpm in reversed(self.recent_wpms)])
                    stdscr.addstr(scoreboard_row, 2, rounds_str)
                
                # Calculate additional stats
                if self.wpm_history:
                    wpms = [h['wpm'] for h in self.wpm_history]
                    accuracies = [h['accuracy'] for h in self.wpm_history]
                    
                    avg_wpm = int(sum(wpms) / len(wpms))
                    top_wpm = max(wpms)  # Top/Best WPM
                    avg_acc = int(sum(accuracies) / len(accuracies))
                    top_acc = max(accuracies)  # Top accuracy
                    
                    # Calculate consistency (standard deviation)
                    if len(wpms) > 1:
                        variance = sum((w - avg_wpm) ** 2 for w in wpms) / len(wpms)
                        std_dev = int(variance ** 0.5)
                        consistency = max(0, 100 - std_dev)  # Higher = more consistent
                    else:
                        consistency = 100
                    
                    # Calculate recent trend (last 10 vs previous)
                    if len(wpms) >= 20:
                        recent_10 = sum(wpms[-10:]) / 10
                        previous_10 = sum(wpms[-20:-10]) / 10
                        trend = recent_10 - previous_10
                        trend_str = f"+{int(trend)}" if trend > 0 else str(int(trend))
                        trend_indicator = "↑" if trend > 0 else "↓" if trend < 0 else "→"
                    else:
                        trend_str = "—"
                        trend_indicator = "→"
                    
                    # Total time practiced (estimate: ~5 seconds per round)
                    total_time_seconds = len(self.wpm_history) * 5
                    hours = total_time_seconds // 3600
                    minutes = (total_time_seconds % 3600) // 60
                    
                    # Display stats in rows
                    stats_line1 = f"Avg: {avg_wpm}wpm | Top: {top_wpm}wpm | Consistency: {consistency}%"
                    stats_line2 = f"Avg Acc: {avg_acc}% | Top Acc: {top_acc}% | Trend: {trend_str}wpm {trend_indicator}"
                    
                    stdscr.addstr(scoreboard_row + 1, 2, stats_line1, curses.A_BOLD)
                    stdscr.addstr(scoreboard_row + 2, 2, stats_line2, curses.A_DIM)
                    
                    # Additional stats if window is tall enough (extended stats)
                    if height > 35:  # Show extra stats if window is tall
                        stats_line3 = f"Total: {len(self.wpm_history)} rounds | Time: {hours}h {minutes}m"
                        stdscr.addstr(scoreboard_row + 3, 2, stats_line3, curses.A_DIM)
            except curses.error:
                pass  # Skip if doesn't fit
        
        # Key difficulty display
        difficulty_row = scoreboard_row + 4  # Adjusted for new stats layout
        if difficulty_row < height - 12:  # Only show if there's room
            try:
                stdscr.addstr(difficulty_row, 2, "Key Difficulty (practice needed):", curses.A_BOLD)
            except curses.error:
                pass
        
        # Sort keys by difficulty (exclude space from difficulty display)
        key_difficulties = [(k, self.stats.get_difficulty_score(k)) 
                           for k in self.stats.unlocked_keys
                           if k != ' ']  # Don't show space in difficulty chart
        key_difficulties.sort(key=lambda x: x[1], reverse=True)
        
        display_count = min(8, len(key_difficulties))
        for i, (key, diff) in enumerate(key_difficulties[:display_count]):
            row = difficulty_row + i + 1
            if row >= height - 3:  # Leave room for instructions
                break
            bar_length = int((diff / 100) * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            acc = self.stats.get_accuracy(key)
            key_str = f"'{key}': {bar} {diff:5.1f} (acc: {acc:5.1f}%)"
            try:
                stdscr.addstr(row, 4, key_str)
            except curses.error:
                pass  # Skip if doesn't fit
        
        # Extended statistics (only show if window is very tall)
        if height > 40 and len(self.wpm_history) > 0:
            extended_row = difficulty_row + display_count + 2
            if extended_row < height - 15:
                try:
                    # Per-key speed histogram header
                    stdscr.addstr(extended_row, 2, "Per-Key Speed Analysis:", curses.A_BOLD)
                    
                    # Show top 5 fastest and slowest keys
                    key_speeds = []
                    for k in self.stats.unlocked_keys:
                        if k.isalpha():
                            if k in self.stats.key_speed and self.stats.key_speed[k]:
                                avg_time = sum(self.stats.key_speed[k]) / len(self.stats.key_speed[k])
                                # Convert ms to chars/sec, then estimate WPM (assuming 5 chars per word)
                                chars_per_sec = 1000 / avg_time if avg_time > 0 else 0
                                wpm = (chars_per_sec * 60) / 5
                                key_speeds.append((k, int(wpm)))
                    
                    if key_speeds:
                        key_speeds.sort(key=lambda x: x[1], reverse=True)
                        
                        # Fastest keys
                        fastest_str = "Fastest: " + " | ".join([f"{k}:{s}wpm" for k, s in key_speeds[:5]])
                        stdscr.addstr(extended_row + 1, 4, fastest_str, curses.color_pair(1))
                        
                        # Slowest keys
                        slowest_str = "Slowest: " + " | ".join([f"{k}:{s}wpm" for k, s in key_speeds[-5:]])
                        stdscr.addstr(extended_row + 2, 4, slowest_str, curses.color_pair(2))
                    
                    # Accuracy streaks
                    stdscr.addstr(extended_row + 4, 2, "Current Session:", curses.A_BOLD)
                    session_str = f"Keys typed: {self.session_keys} | Errors: {self.session_errors} | Session Accuracy: {int((1 - self.session_errors / max(self.session_keys, 1)) * 100)}%"
                    stdscr.addstr(extended_row + 5, 4, session_str, curses.A_DIM)
                    
                except (curses.error, AttributeError, KeyError):
                    pass  # Skip if error or attributes don't exist
        
        # Instructions
        instr_row = height - 3
        
        # WPM graph if we have history
        if self.wpm_history and len(self.wpm_history) >= 2 and height > instr_row + 2:
            graph_row = instr_row - 12
            if graph_row > difficulty_row + 10:  # Only show if there's room
                try:
                    import asciichartpy
                    
                    # Take ALL history and bucket into 50 points
                    all_history = self.wpm_history
                    num_buckets = 50
                    
                    if len(all_history) <= num_buckets:
                        # If we have fewer than 50 rounds, just use them all
                        wpms = [h['wpm'] for h in all_history]
                    else:
                        # Divide all data into 50 buckets and average each bucket
                        bucket_size = len(all_history) / num_buckets
                        wpms = []
                        for i in range(num_buckets):
                            start_idx = int(i * bucket_size)
                            end_idx = int((i + 1) * bucket_size)
                            bucket_data = all_history[start_idx:end_idx]
                            if bucket_data:
                                avg_wpm = sum(h['wpm'] for h in bucket_data) / len(bucket_data)
                                wpms.append(avg_wpm)
                    
                    # Generate smooth line chart
                    chart_config = {
                        'height': 8,
                        'format': '{:8.0f}',
                    }
                    
                    chart = asciichartpy.plot(wpms, chart_config)
                    chart_lines = chart.split('\n')
                    
                    # Display header with total rounds
                    try:
                        stdscr.addstr(graph_row, 2, f"WPM Progress - All Time ({len(all_history)} rounds):", curses.A_BOLD)
                    except curses.error:
                        pass
                    
                    # Display chart with green color
                    for i, line in enumerate(chart_lines):
                        if graph_row + i + 1 < instr_row:
                            try:
                                # Limit width to prevent overflow
                                display_line = line[:min(len(line), width - 4)]
                                stdscr.addstr(graph_row + i + 1, 2, display_line, curses.color_pair(1))
                            except curses.error:
                                pass
                    
                except ImportError:
                    # Fallback to basic chart if library not installed
                    all_history = self.wpm_history
                    num_buckets = 50
                    
                    if len(all_history) <= num_buckets:
                        wpms = [h['wpm'] for h in all_history]
                    else:
                        bucket_size = len(all_history) / num_buckets
                        wpms = []
                        for i in range(num_buckets):
                            start_idx = int(i * bucket_size)
                            end_idx = int((i + 1) * bucket_size)
                            bucket_data = all_history[start_idx:end_idx]
                            if bucket_data:
                                avg_wpm = sum(h['wpm'] for h in bucket_data) / len(bucket_data)
                                wpms.append(int(avg_wpm))
                    
                    min_wpm = max(0, min(wpms) - 5)
                    max_wpm = max(wpms) + 5
                    wpm_range = max(max_wpm - min_wpm, 1)
                    
                    graph_height = 8
                    graph_width = min(70, width - 6)
                    
                    try:
                        stdscr.addstr(graph_row, 2, f"WPM Progress - All Time ({len(all_history)} rounds):", curses.A_BOLD)
                        stdscr.addstr(graph_row + graph_height + 2, 2, "Tip: pip3 install asciichartpy --break-system-packages for smoother chart", curses.A_DIM)
                    except curses.error:
                        pass
                    
                    # Simple bar chart fallback
                    graph = [[' ' for _ in range(graph_width)] for _ in range(graph_height)]
                    
                    for i, wpm in enumerate(wpms):
                        x = int((i / max(len(wpms) - 1, 1)) * (graph_width - 1))
                        normalized_height = int(((wpm - min_wpm) / wpm_range) * (graph_height - 1))
                        
                        for y in range(graph_height - 1, graph_height - 1 - normalized_height - 1, -1):
                            if 0 <= x < graph_width and 0 <= y < graph_height:
                                graph[y][x] = '│'
                    
                    for i, row in enumerate(graph):
                        try:
                            stdscr.addstr(graph_row + i + 1, 4, ''.join(row), curses.color_pair(1))
                        except curses.error:
                            pass
                    
                    try:
                        stdscr.addstr(graph_row + 1, 2, f"{int(max_wpm)}", curses.A_DIM)
                        stdscr.addstr(graph_row + graph_height, 2, f"{int(min_wpm)}", curses.A_DIM)
                    except curses.error:
                        pass
                        
                except curses.error:
                    pass
        
        try:
            stdscr.addstr(instr_row, 2, "Backspace: restart | Ctrl+C: quit | Cmd+/-: font size | Resize terminal for more stats", curses.A_DIM)
        except curses.error:
            pass
        
        stdscr.refresh()
    
    def run(self, stdscr):
        """Main run loop"""
        # Setup colors
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Correct
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # Error
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Current
        
        curses.curs_set(0)  # Hide cursor
        stdscr.timeout(50)  # 50ms = 20 FPS (was 100ms), reduces flashing
        
        # Enable nodelay for smoother input
        stdscr.nodelay(True)
        
        self.stats.session_count += 1
        self.start_new_text()
        
        last_draw_time = time.time()
        draw_interval = 0.05  # Redraw at most every 50ms
        
        while True:
            try:
                # Only redraw if enough time has passed (prevents flashing)
                current_time = time.time()
                if current_time - last_draw_time >= draw_interval:
                    self.draw_interface(stdscr)
                    last_draw_time = current_time
                
                key = stdscr.getch()
                
                if key == -1:  # No input
                    continue
                elif key == curses.KEY_RESIZE:  # Terminal resized
                    stdscr.clear()
                    self.draw_interface(stdscr)
                    continue
                elif key == 3:  # Ctrl+C
                    break
                elif key == curses.KEY_BACKSPACE or key == 127:  # Backspace
                    self.start_new_text()
                    self.draw_interface(stdscr)  # Immediate redraw on action
                elif 32 <= key <= 126:  # Printable characters
                    char = chr(key)
                    completed = self.process_key(char)
                    
                    self.draw_interface(stdscr)  # Immediate redraw on keystroke
                    
                    if completed:
                        # Small delay to show completion
                        time.sleep(0.3)
                        self.start_new_text()
            
            except KeyboardInterrupt:
                break
            except curses.error:
                # Ignore curses errors (usually from terminal resize)
                stdscr.clear()
                continue
        
        # Save stats on exit
        self.stats.save_stats()

def main():
    """Main entry point"""
    app = TypingApp()
    try:
        curses.wrapper(app.run)
    except KeyboardInterrupt:
        print("\nSaving progress...")
        app.stats.save_stats()
        print("Thanks for practicing! Come back soon.")

if __name__ == "__main__":
    main()
