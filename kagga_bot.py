#!/usr/bin/env python3

"""
Mastodon Kagga Bot
==================
Posts all 945 Mankutimmana Kagga verses by D.V. Gundappa (DVG)
to a Mastodon account on a configurable schedule.

Each post includes:
- Kannada verse
- Roman transliteration
- English explanation
- Hashtags

When a post exceeds 500 chars, it splits into a thread:
  Post 1 (below) -> English explanation
  Post 2 (top)   -> Kannada verse + transliteration + tags

Verse selection is stateless: computed from START_DATE and START_VERSE
in config.py. No state.json needed. Safe to run on ephemeral platforms
like GitHub Actions.

Usage:
  python kagga_bot.py              # Start the scheduler (daemon mode)
  python kagga_bot.py --post-now   # Post one verse immediately and exit
  python kagga_bot.py --dry-run    # Preview without sending
  python kagga_bot.py --verse N    # Post a specific verse number (1-945)
  python kagga_bot.py --list-themes
"""

import argparse
import logging
import os
import random
import sys
import time
from datetime import datetime, timedelta, timezone

try:
    from mastodon import Mastodon, MastodonError
except ImportError:
    print("ERROR: Run: pip install --user Mastodon.py")
    sys.exit(1)

import config
from kagga_verses import KAGGA_VERSES

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

handlers = [logging.StreamHandler(sys.stdout)]
try:
    handlers.append(logging.FileHandler(config.LOG_FILE, encoding="utf-8"))
except OSError:
    pass

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)-8s %(message)s",
    handlers=handlers,
)
log = logging.getLogger("kagga_bot")

# ---------------------------------------------------------------------------
# Verse lookup
# ---------------------------------------------------------------------------

_BY_NUMBER = {v["number"]: v for v in KAGGA_VERSES}

_BY_THEME = {}
for _v in KAGGA_VERSES:
    for _t in _v.get("themes", []):
        for _word in _t.split():
            _w = _word.strip().lower()
            if _w:
                _BY_THEME.setdefault(_w, []).append(_v)

# ---------------------------------------------------------------------------
# Stateless verse selection
#
# START_DATE and START_VERSE are set in config.py.
# Every 12 hours from START_DATE, the next verse is posted sequentially.
# This computation is deterministic: any run at any time produces the
# correct verse without needing a state file.
# ---------------------------------------------------------------------------

TOTAL_VERSES = len(KAGGA_VERSES)  # 945
INTERVAL_HOURS = 12

def compute_current_verse():
    now = datetime.now(timezone.utc)
    start = config.START_DATE.replace(tzinfo=timezone.utc)

    days_elapsed = (now - start).days  # whole days only, no float precision issues
    
    # Which of the two daily posts is this? Check the hour.
    post_number = 1 if now.hour >= 18 else 0

    posts_since_start = (days_elapsed * 2) + post_number

    verse_number = (posts_since_start % TOTAL_VERSES) + 1

    log.info(
        "Day %d | Post %d | Computed verse: #%d",
        days_elapsed, post_number, verse_number
    )
    return  _BY_NUMBER.get(verse_number)


# ---------------------------------------------------------------------------
# Verse selection (unified entry point)
# ---------------------------------------------------------------------------

def pick_verse(specific=None, theme=None):
    if specific is not None:
        v = _BY_NUMBER.get(specific)
        if not v:
            log.error("Verse %d not found.", specific)
            sys.exit(1)
        return v

    if theme:
        pool = _BY_THEME.get(theme.lower(), KAGGA_VERSES)
        return random.choice(pool)

    # Default: stateless date-math selection
    return compute_current_verse()


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

def build_tags(verse, short=False):
    if short:
        return "#Kagga #DVG"
    base = ["#Kagga", "#DVG", "#KannadaPoetry", "#MankutimmanaKagga"]
    return " ".join(base)


# ---------------------------------------------------------------------------
# Post composition
# ---------------------------------------------------------------------------

LIMIT = 500


def build_single(verse, short=False):
    """Single post: verse + transliteration + explanation + tags."""
    num = str(verse.get("number", ""))
    tags = build_tags(verse, short=short)
    trans = verse.get("transliteration", "").strip()
    expl = verse.get("explanation", "").strip()
    kv = verse["verse"].strip()

    parts = []
    if num:
        parts += ["#" + num, ""]
    parts.append(kv)
    if trans:
        parts += ["", trans]
    if expl:
        parts += ["", expl]
    parts += ["", tags]
    return "\n".join(parts)


def build_thread(verse):
    """
    Two-post thread for long posts.
    Post 1 (older, appears below) -> explanation
    Post 2 (newer, appears on top) -> verse + transliteration + tags
    """
    expl = verse.get("explanation", "").strip()
    num = str(verse.get("number", ""))
    tags = build_tags(verse, short=True)
    trans = verse.get("transliteration", "").strip()
    kv = verse["verse"].strip()

    p1 = ("💡 " + expl) if expl else ""

    p2_parts = []
    if num:
        p2_parts += ["#" + num, ""]
    p2_parts.append(kv)
    if trans:
        p2_parts += ["", trans]
    p2_parts += ["", tags]
    p2 = "\n".join(p2_parts)

    return p1, p2


# ---------------------------------------------------------------------------
# Mastodon client
# ---------------------------------------------------------------------------

def get_client():
    token = os.environ.get("MASTODON_ACCESS_TOKEN") or config.MASTODON_ACCESS_TOKEN
    if not token or token == "YOUR_ACCESS_TOKEN_HERE":
        log.error("Set MASTODON_ACCESS_TOKEN in config.py or as an environment variable.")
        sys.exit(1)
    return Mastodon(
        access_token=token,
        api_base_url=config.MASTODON_INSTANCE_URL,
    )


# ---------------------------------------------------------------------------
# Post
# ---------------------------------------------------------------------------

def post_verse(dry_run=False, specific=None, theme=None):
    verse = pick_verse(specific=specific, theme=theme)
    if verse is None:
        log.error("Could not resolve a verse to post.")
        sys.exit(1)

    num = verse.get("number", "?")

    # Try 1: single post with full tags
    text = build_single(verse, short=False)

    # Try 2: single post with short tags
    if len(text) > LIMIT:
        text = build_single(verse, short=True)

    # Try 3: thread
    thread = len(text) > LIMIT
    if thread:
        p1, p2 = build_thread(verse)
        log.info("-" * 50)
        log.info("Verse #%s THREAD", num)
        log.info("Post 1 (%d chars):\n%s", len(p1), p1)
        log.info("Post 2 (%d chars):\n%s", len(p2), p2)
    else:
        log.info("-" * 50)
        log.info("Verse #%s (%d chars):\n%s", num, len(text), text)

    if dry_run or config.DRY_RUN:
        log.info("[DRY RUN] Not posted.")
        return

    try:
        client = get_client()
        if thread:
            s1 = client.status_post(status=p1, visibility=config.POST_VISIBILITY)
            log.info("Posted 1: %s", s1["url"])
            if p2:
                s2 = client.status_post(
                    status=p2,
                    in_reply_to_id=s1["id"],
                    visibility=config.POST_VISIBILITY,
                )
                log.info("Posted 2: %s", s2["url"])
        else:
            s = client.status_post(status=text, visibility=config.POST_VISIBILITY)
            log.info("Posted: %s", s["url"])

    except MastodonError as exc:
        log.error("Mastodon error: %s", exc)
    except Exception as exc:
        log.error("Unexpected error: %s", exc)


# ---------------------------------------------------------------------------
# Scheduler (daemon mode — not used on GitHub Actions)
# ---------------------------------------------------------------------------

def wait_seconds():
    unit = config.POSTING_INTERVAL_UNIT
    value = config.POSTING_INTERVAL_VALUE
    now = datetime.now()

    if unit == "minutes":
        return value * 60
    if unit == "hours":
        return value * 3600
    if unit == "days":
        h, m = map(int, config.SCHEDULED_TIME.split(":"))
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=value)
        return (target - now).total_seconds()
    raise ValueError("POSTING_INTERVAL_UNIT must be: minutes, hours, or days")


def run_scheduler():
    log.info("Kagga Bot starting — %d verses loaded", len(KAGGA_VERSES))
    log.info("Instance  : %s", config.MASTODON_INSTANCE_URL)
    log.info("Schedule  : every %d %s", config.POSTING_INTERVAL_VALUE, config.POSTING_INTERVAL_UNIT)
    log.info("Start date: %s | Start verse: #%d", config.START_DATE.date(), config.START_VERSE)

    post_verse()

    while True:
        secs = wait_seconds()
        next_at = datetime.now() + timedelta(seconds=secs)
        log.info("Next post at %s", next_at.strftime("%Y-%m-%d %H:%M:%S"))
        time.sleep(secs)
        post_verse()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def list_themes():
    print("\nAvailable themes:")
    for t in sorted(_BY_THEME.keys()):
        print("  %-20s (%d verses)" % (t, len(_BY_THEME[t])))


def main():
    parser = argparse.ArgumentParser(description="Mastodon Kagga Bot")
    parser.add_argument("--post-now", action="store_true", help="Post one verse and exit")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    parser.add_argument("--verse", type=int, default=None, help="Post specific verse (1-945)")
    parser.add_argument("--theme", type=str, default=None, help="Post random verse from theme")
    parser.add_argument("--list-themes", action="store_true", help="List all themes")
    args = parser.parse_args()

    if args.list_themes:
        list_themes()
    elif args.post_now or args.dry_run or args.verse or args.theme:
        post_verse(dry_run=args.dry_run, specific=args.verse, theme=args.theme)
    else:
        run_scheduler()


if __name__ == "__main__":
    main()
