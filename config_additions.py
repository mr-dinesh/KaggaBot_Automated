# Add these two lines to your existing config.py

from datetime import datetime

# The date you are deploying this bot (today). Verse #7 will post at this moment,
# verse #8 twelve hours later, and so on. All times are UTC.
START_DATE = datetime(2026, 3, 24, 0, 0, 0)   # today — adjust hour to now if needed

# The first verse to post. Previous verses (1-6) are skipped.
START_VERSE = 7
