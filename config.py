# =============================================================================
#  Mastodon Kagga Bot — Configuration
#  Edit this file, or override any setting via environment variables.
# =============================================================================

import os

# ---------------------------------------------------------------------------
# Mastodon credentials
# 1. Create a bot account on your Mastodon instance
# 2. Go to Settings -> Development -> New Application
# 3. Enable scope: write:statuses
# 4. Copy "Your access token" and paste below
# ---------------------------------------------------------------------------
MASTODON_INSTANCE_URL = os.getenv("MASTODON_INSTANCE_URL", "https://mastodon.social")
MASTODON_ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN_HERE")

# ---------------------------------------------------------------------------
# Posting schedule
# POSTING_INTERVAL_UNIT  : "minutes" | "hours" | "days"
# POSTING_INTERVAL_VALUE : integer
#
# Examples:
#   Every 6 hours   ->  UNIT="hours",   VALUE=6
#   Twice a day     ->  UNIT="hours",   VALUE=12
#   Once a day      ->  UNIT="days",    VALUE=1  (posts at SCHEDULED_TIME)
#   Every 30 min    ->  UNIT="minutes", VALUE=30
# ---------------------------------------------------------------------------
POSTING_INTERVAL_UNIT  = os.getenv("POSTING_INTERVAL_UNIT",  "hours")
POSTING_INTERVAL_VALUE = int(os.getenv("POSTING_INTERVAL_VALUE", "12"))

# Used only when POSTING_INTERVAL_UNIT == "days" (24-hour HH:MM, server time)
SCHEDULED_TIME = os.getenv("SCHEDULED_TIME", "08:00")

# ---------------------------------------------------------------------------
# Verse ordering
# "sequential" -> cycles through all 945 in order (state saved in STATE_FILE)
# "random"     -> picks a random verse each time
# ---------------------------------------------------------------------------
VERSE_ORDER = os.getenv("VERSE_ORDER", "sequential")
STATE_FILE  = os.getenv("STATE_FILE",  "bot_state.json")

# ---------------------------------------------------------------------------
# Post visibility: "public" | "unlisted" | "private" | "direct"
# ---------------------------------------------------------------------------
POST_VISIBILITY = os.getenv("POST_VISIBILITY", "public")

# ---------------------------------------------------------------------------
# Misc
# DRY_RUN=true prints posts to console without sending
# ---------------------------------------------------------------------------
DRY_RUN   = os.getenv("DRY_RUN",   "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE  = os.getenv("LOG_FILE",  "kagga_bot.log")


##

DRY_RUN   = os.getenv("DRY_RUN",   "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE  = os.getenv("LOG_FILE",  "kagga_bot.log")

from datetime import datetime, timezone


START_DATE = datetime(2026, 3, 27, 0, 0, 0, tzinfo=timezone.utc)  # today
START_VERSE = 10  # unused now, but keep it for reference