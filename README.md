# 📜 Mastodon Kagga Bot

Posts all 945 Mankutimmana Kagga verses by **D.V. Gundappa (DVG)** to Mastodon
on a configurable schedule.

---

## Files

```
kagga_bot/
├── kagga_bot.py      ← Main bot (run this)
├── kagga_verses.py   ← All 945 verses (Kannada + transliteration + explanation)
├── config.py         ← All settings — edit this first
├── requirements.txt  ← Dependencies
└── README.md
```

---

## Setup

### 1. Create a virtual environment & install

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure credentials

Edit `config.py`:

```python
MASTODON_INSTANCE_URL = "https://botsin.space"   # your instance
MASTODON_ACCESS_TOKEN = "your_token_here"         # from Settings → Development
```

### 3. Set your posting schedule

| Goal | Settings in config.py |
|------|----------------------|
| Every 6 hours | `POSTING_INTERVAL_UNIT="hours"`, `VALUE=6` |
| Once a day at 8 AM | `POSTING_INTERVAL_UNIT="days"`, `VALUE=1`, `SCHEDULED_TIME="08:00"` |
| Every 30 minutes | `POSTING_INTERVAL_UNIT="minutes"`, `VALUE=30` |

---

## Running

```bash
# Preview a post (no network call)
python kagga_bot.py --dry-run

# Post verse #1 as a test
python kagga_bot.py --verse 1 --dry-run

# Send a real test post
python kagga_bot.py --post-now

# Start the scheduler (runs forever)
python kagga_bot.py

# Post a verse from a specific theme
python kagga_bot.py --theme Wisdom --post-now

# See all available themes
python kagga_bot.py --list-themes
```

---

## PythonAnywhere deployment

```bash
# In PythonAnywhere Bash console:
mkdir ~/kagga_bot && cd ~/kagga_bot
# Upload all 4 files via the Files tab, then:
pip install --user Mastodon.py

# Test
python kagga_bot.py --dry-run
```

In the **Tasks** tab, add a scheduled task:
```
python /home/yourusername/kagga_bot/kagga_bot.py --post-now
```

---

## Sample post

```
📖 Kagga #943

ಬೇಡಿದುದನೀವನೀಶ್ವರನೆಂಬ ನೆಚ್ಚಿಲ್ಲ ।
ಬೇಡಲೊಳಿತಾವುದೆಂಬುದರರಿವುಮಿಲ್ಲ ॥
ಕೂಡಿಬಂದುದನೆ ನೀನ್ ಅವನಿಚ್ಛೆಯೆಂದು ಕೊಳೆ ।
ನೀಡುಗೆದೆಗಟ್ಟಿಯನು - ಮಂಕುತಿಮ್ಮ ॥ ೯೪೩ ॥

💡 There is no guarantee that God will grant all our wishes.
   Face all circumstances with a strong heart. - Mankutimma

#Kagga #DVG #KannadaPoetry #ಕಗ್ಗ #Devotion #Morality #Love
```

---

## Environment variable overrides

All `config.py` values can be set as env vars (useful for Docker/systemd):

```bash
export MASTODON_ACCESS_TOKEN="your_token"
export MASTODON_INSTANCE_URL="https://botsin.space"
export POSTING_INTERVAL_UNIT="hours"
export POSTING_INTERVAL_VALUE="6"
export VERSE_ORDER="sequential"
export DRY_RUN="false"
python kagga_bot.py
```
