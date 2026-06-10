# 📦 English Dialogue Trainer Pro — Premium Edition

A complete premium redesign of the English Dialogue Trainer for warehouse/logistics professionals. Built with Streamlit and featuring a professional dark theme, gamification system, and modern UI components.

## ✨ Premium Features

### 🎨 Visual Design
- **Dark glassmorphism theme** with gradient accents
- **Custom typography** (Inter + JetBrains Mono)
- **Animated cards** with hover effects and glow
- **Responsive layout** optimized for all screen sizes
- **Smooth animations** (fade-ins, pulses, shimmer effects)

### 🏆 Gamification System
- **6 Career Levels**: Novice → Clerk → Supervisor → Manager → Director → Executive
- **XP Progression** with visual progress bars
- **Streak Counter** with flame animation
- **Achievement System** with 7 unlockable badges:
  - 🎯 First Steps
  - 🔥 On Fire (5 streak)
  - ⚡ Unstoppable (10 streak)
  - 📚 Word Collector (50 vocab)
  - 🎓 Lexicon Master (100 vocab)
  - 📅 Week Warrior (7-day streak)
  - 🎙️ Voice Master (10 audio uses)

### 🧠 Smart Learning
- **Adaptive difficulty** with 3 levels (Easy/Medium/Hard)
- **Spaced repetition** for difficult words (30% chance to revisit)
- **Similarity scoring** with detailed feedback
- **Audio transcription** with speech recognition
- **Text-to-speech** for pronunciation practice

### 📊 Analytics
- **Real-time stats** dashboard (XP, Level, Streak, Score)
- **History table** with similarity progress bars
- **Difficulty tracking** per exercise
- **Performance feedback** with color-coded messages

## 🚀 Installation

```bash
# Install dependencies
pip install streamlit gtts speechrecognition audio-recorder-streamlit pandas

# Run the app
streamlit run english_trainer_premium.py
```

## 📁 File Structure

```
english_trainer_premium.py    # Main application (premium version)
user_progress.json            # User data (auto-generated)
frases.json                   # Your custom phrases (optional)
Vocabulario.json              # Your custom vocabulary (optional)
```

## 🎮 How to Use

1. **Select Difficulty**: Choose between Easy (with PT translation), Medium (toggle translation), or Hard (English only)
2. **Read/Listen**: View the English question and click to hear pronunciation
3. **Respond**: Type your answer or use the microphone
4. **Get Feedback**: Receive instant scoring with XP rewards
5. **Track Progress**: Watch your level, streak, and achievements grow
6. **Practice Vocabulary**: Browse topic-based word lists with audio

## 🛠️ Customization

### Adding Your Own Content

Replace `SAMPLE_FRASES` and `SAMPLE_VOCAB` with your JSON files:

```python
# Load from files
with open("frases.json", "r", encoding="utf-8") as f:
    frases_por_nivel = json.load(f)

with open("Vocabulario.json", "r", encoding="utf-8") as f:
    Vocabulario = json.load(f)
```

### Modifying the Theme

Edit the CSS in `inject_custom_css()` to change colors:
- Primary: `#6366f1` (Indigo)
- Success: `#10b981` (Emerald)
- Warning: `#f59e0b` (Amber)
- Danger: `#ef4444` (Red)

### Adjusting Level System

Modify the `LEVELS` dictionary to change XP requirements:

```python
LEVELS = {
    1: {"name": "Novice", "icon": "🌱", "xp_needed": 0},
    2: {"name": "Clerk", "icon": "📋", "xp_needed": 100},
    # ... add more levels
}
```

## 🔒 Data Persistence

User progress is automatically saved to `user_progress.json`:
- XP and level progression
- Achievement unlocks
- Streak history
- Difficult words tracking
- Vocabulary seen

## 📱 Mobile Support

The app is fully responsive and works on mobile devices:
- Touch-friendly buttons
- Optimized text sizes
- Audio recording support on mobile browsers

## 🎯 Premium vs Original

| Feature | Original | Premium |
|---------|----------|---------|
| Visual Design | Default Streamlit | Custom dark glassmorphism |
| Gamification | Basic score | XP, levels, achievements |
| Feedback | Simple text | Animated color-coded cards |
| Audio | Basic player | Styled with wave animation |
| Progress | JSON dump | Visual dashboard |
| Vocabulary | Plain list | Animated cards with topics |
| History | Basic table | Styled with progress bars |

## 🤝 Contributing

Feel free to fork and customize for your specific warehouse terminology or industry needs.

---

**Built with ❤️ for warehouse professionals learning English**
