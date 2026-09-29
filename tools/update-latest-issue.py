#!/usr/bin/env python3
"""Rewrite the "Latest issue" card in index.html from the Promptwrought feed.

Run by .github/workflows/latest-issue.yml on Tuesdays, or by hand:

    python3 tools/update-latest-issue.py            # update index.html
    python3 tools/update-latest-issue.py --dry-run  # show the card, change nothing

It reads the newest post from the Substack feed, finds its issue number
from the file names in promptwrought-site/issues, and replaces only what
sits between the latest-issue start and end markers in index.html.
If anything is missing or looks wrong it changes nothing, says what the
problem is and exits with an error: a half-filled card is never written.

Exit codes:
    0   the card was updated, or was already current
    1   a check failed, so nothing was changed
    75  the post is out but its issue file isn't in promptwrought-site yet:
        try again later. (75 is the usual "temporary failure" code, and
        it can't be mistaken for Python's own errors, which use 1 and 2.)

Standard library only. It runs on the Mac's Python 3.9 as well as the
newer Python on GitHub's runners.
"""

import argparse
import hashlib
import html
import http.client
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# ---------- Where things live ----------
FEED_URL = "https://promptwrought.substack.com/feed"
ISSUES_URL = "https://api.github.com/repos/emmadarlingt-hue/promptwrought-site/contents/issues"
POST_HOST = "promptwrought.substack.com"   # the only site the card may link to
PAGE = Path(__file__).resolve().parent.parent / "index.html"

# The card lives between these two comments in index.html.
START = "<!-- latest-issue:start -->"
END = "<!-- latest-issue:end -->"

# Issue files are named like "009-verifidget.json": the number, a hyphen,
# the word, ".json". Group 1 is the number, group 2 the word.
ISSUE_FILE = re.compile(r"(\d{3,})-([a-z0-9-]+)\.json")

# Substack's month style, as the card has always shown it: "22 Sept 2026".
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "June",
          "July", "Aug", "Sept", "Oct", "Nov", "Dec"]

LONDON = ZoneInfo("Europe/London")
MAX_BYTES = 5_000_000   # far more than the feed needs; anything bigger is wrong


class CheckFailed(Exception):
    """A problem that means the card must not change. Exit code 1."""
    exit_code = 1


class IssueFileMissing(CheckFailed):
    """The post is out, but its issue file hasn't been committed to
    promptwrought-site yet. A later run will try again. Exit code 75."""
    exit_code = 75


class KeepTokenOnGitHub(urllib.request.HTTPRedirectHandler):
    """Follow redirects as usual, but if one leads away from GitHub's
    API, drop the token first. Python would otherwise copy it onto the
    new request, whatever site that request is going to."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and urllib.parse.urlsplit(newurl).hostname != "api.github.com":
            new.remove_header("Authorization")
        return new


def parse_args():
    """Read the command-line options. The defaults are the real feed,
    GitHub's live list of issue files and this repo's index.html; the
    options exist so the checks can be tried on saved test files."""
    parser = argparse.ArgumentParser(
        description="Rewrite the Latest issue card in index.html from the Promptwrought feed.")
    parser.add_argument("--feed", default=FEED_URL,
                        help="feed address, or file:// for a saved copy")
    parser.add_argument("--issues", default=ISSUES_URL,
                        help="GitHub's list of issue files: an address or a saved JSON file")
    parser.add_argument("--page", default=str(PAGE),
                        help="the page to update (default: this repo's index.html)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the card and change nothing")
    return parser.parse_args()


def fetch(source, what):
    """Download an address (or read a local file) and return its bytes.
    It tries three times, a few seconds apart, because a runner's first
    request can fail for reasons that have nothing to do with us. The
    GitHub token, when there is one, is only ever sent to GitHub's API,
    and it is never printed."""
    if "://" not in source:  # a plain file path, for testing
        try:
            return Path(source).read_bytes()
        except OSError as error:
            raise CheckFailed(f"Couldn't read the {what} from {source}: {error.strerror}")

    headers = {"User-Agent": "emmadarling.dev latest-issue updater"}
    if urllib.parse.urlsplit(source).hostname == "api.github.com":
        headers["Accept"] = "application/vnd.github+json"
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

    opener = urllib.request.build_opener(KeepTokenOnGitHub)
    problem = None
    for attempt in range(3):
        if attempt:
            time.sleep(5)
        try:
            request = urllib.request.Request(source, headers=headers)
            with opener.open(request, timeout=20) as response:
                body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                raise CheckFailed(f"The {what} is over 5 MB, which can't be right")
            return body
        except urllib.error.HTTPError as error:
            problem = f"HTTP {error.code}"
            if error.code < 500 and error.code not in (403, 429):
                break   # a 404 won't fix itself; 403/429 are rate limits, worth a retry
        except (urllib.error.URLError, OSError, http.client.HTTPException) as error:
            # HTTPException covers a download cut off part-way (IncompleteRead)
            problem = str(getattr(error, "reason", None) or repr(error))
    raise CheckFailed(f"Couldn't read the {what} ({source}): {problem}")


def parse_date(text):
    """Turn an RSS date like "Tue, 22 Sep 2026 12:33:02 GMT" into a time
    in UTC, or None if it's missing or can't be read. Python 3.9 and
    newer versions fail in different ways on a bad date, so all of them
    are caught. A date with no time zone is taken as UTC."""
    if not text or not text.strip():
        return None
    try:
        when = parsedate_to_datetime(text.strip())
    except (TypeError, ValueError, IndexError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when.astimezone(timezone.utc)


def clean_text(text, field):
    """Tidy one field from the feed: turn entities like &#8212; into the
    characters they stand for, squash runs of spaces and line breaks
    into single spaces, and trim the ends. An empty result, or one that
    still contains a tag, stops the update."""
    tidy = " ".join(html.unescape(text or "").split())
    if not tidy:
        raise CheckFailed(f"The newest post has no {field}: it's empty in the feed")
    if "<" in tidy:
        raise CheckFailed(f"The newest post's {field} contains markup ({tidy[:60]!r}), not plain text")
    return tidy


def check_word(title):
    """The post's title is the coined word. It must start with a letter
    and use only letters, digits and single hyphens (the same characters
    the issue file names allow), because it ends up in a branch name and
    a pull request title as well as on the page."""
    word = title.lower()
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", word):
        raise CheckFailed(f"The newest post's title {title!r} isn't a single coined word "
                          "(letters, digits and hyphens, starting with a letter)")
    return word


def check_link(url):
    """The card's link must be an https address for a post on the
    newsletter's own Substack. Anything else (plain http, another site,
    a moved domain) stops the update rather than going live. Any query
    or fragment is dropped."""
    parts = urllib.parse.urlsplit(url)
    if (parts.scheme != "https" or parts.hostname != POST_HOST
            or not re.fullmatch(r"/p/[a-z0-9-]+/?", parts.path)):
        raise CheckFailed(f"The newest post's link {url!r} isn't an https link to a post on {POST_HOST}")
    return urllib.parse.urlunsplit(("https", POST_HOST, parts.path, "", ""))


def read_newest_post(feed):
    """Find the newest post in the RSS feed and return its word,
    definition, link and publication time, each cleaned and checked.
    The feed lists the newest first, but the dates are compared anyway,
    so every post needs a readable date."""
    if b"<!doctype" in feed[:2000].lower():
        raise CheckFailed("The feed starts with a DOCTYPE: that's a web page (an error or a "
                          "robot check), not Substack's RSS")
    try:
        root = ET.fromstring(feed)
    except ET.ParseError as error:
        raise CheckFailed(f"The feed isn't readable XML ({error})")

    items = root.findall("./channel/item")
    if not items:
        raise CheckFailed("The feed has no posts in it")
    dated = []
    for item in items:
        published = parse_date(item.findtext("pubDate"))
        if published is None:
            title = (item.findtext("title") or "").strip() or "(untitled)"
            raise CheckFailed(f"The post {title!r} has no readable date (pubDate), "
                              "so the newest post can't be picked safely")
        dated.append((published, item))
    published, newest = max(dated, key=lambda pair: pair[0])

    return {
        "word": check_word(clean_text(newest.findtext("title"), "title")),
        "definition": clean_text(newest.findtext("description"), "definition (description)"),
        "link": check_link(clean_text(newest.findtext("link"), "link")),
        "published": published,
    }


def list_issue_files(listing):
    """Read GitHub's listing of promptwrought-site/issues and return the
    file names. If GitHub sent something other than a list of files
    (a rate-limit message, say), stop."""
    try:
        entries = json.loads(listing)
    except ValueError:
        raise CheckFailed("GitHub's list of issue files isn't readable JSON")
    if not isinstance(entries, list):
        message = entries.get("message") if isinstance(entries, dict) else None
        raise CheckFailed("GitHub didn't send the list of issue files"
                          + (f": {message}" if message else ""))
    return [entry.get("name", "") for entry in entries
            if isinstance(entry, dict) and entry.get("type") == "file"]


def find_issue_number(word, filenames):
    """Work out the issue number for a word from the promptwrought-site
    file names, which look like "009-verifidget.json".

    Returns the number as an int (9 for "009-verifidget.json").
    Raises IssueFileMissing if no file matches the word yet: the post
    can go out before its file is committed, and a later run will try
    again. Raises CheckFailed if more than one file matches, because
    then the number would be a guess."""
    matches = []
    for name in filenames:
        m = ISSUE_FILE.fullmatch(name)
        if m and m.group(2) == word:
            matches.append(name)
    if not matches:
        raise IssueFileMissing(f"No file in promptwrought-site/issues matches '{word}'")
    if len(matches) > 1:
        raise CheckFailed(f"More than one issue file for '{word}': {', '.join(matches)}")
    return int(ISSUE_FILE.fullmatch(matches[0]).group(1))


def london_date(published):
    """The date on the card is the day it was in London when the post
    went out, not the day in UTC (the two differ just after midnight)."""
    return published.astimezone(LONDON).date()


def format_card_date(day):
    """Write a date the way the card always has: "22 Sept 2026". The
    month names are spelled out here rather than taken from the
    computer's language settings, which vary from machine to machine."""
    return f"{day.day} {MONTHS[day.month - 1]} {day.year}"


def build_card(issue, indent):
    """Build the card's HTML, one line at a time, indented to sit under
    the start marker. It's the markup the page's script used to build:
    the eyebrow, the word, its definition, "Issue 009 · 22 Sept 2026"
    with the date in a <time> element, and one external link whose
    screen-reader name includes the word. Every value from the feed is
    escaped, so text can never turn into HTML.
    The link follows the same pattern as makeCardLink() and
    makeArrowLink() in index.html's script: change both together."""
    def esc(value):
        return html.escape(str(value), quote=True)

    day = issue["date"]
    lines = [
        '<article class="card">',
        '  <p class="eyebrow">Latest issue</p>',
        f'  <h3>{esc(issue["word"])}</h3>',
        f'  <p class="card-summary">{esc(issue["definition"])}</p>',
        f'  <p class="card-meta">Issue {issue["number"]:03d} · '
        f'<time datetime="{day.isoformat()}">{format_card_date(day)}</time></p>',
        f'  <p class="card-links"><a href="{esc(issue["link"])}" '
        f'aria-label="Read the issue: {esc(issue["word"])}" target="_blank" '
        f'rel="noopener noreferrer">Read the issue<span aria-hidden="true"> →</span></a></p>',
        '</article>',
    ]
    return "\n".join(indent + line for line in lines)


def find_card_region(page):
    """Find the one start marker and the one end marker, in that order.
    Returns where the card between them begins and ends, and the indent
    of the start marker's line, so the new card lines up under it."""
    starts, ends = page.count(START), page.count(END)
    if starts != 1 or ends != 1:
        raise CheckFailed(f"index.html needs exactly one start and one end marker "
                          f"(found {starts} start, {ends} end)")
    start, end = page.index(START), page.index(END)
    if end < start:
        raise CheckFailed("In index.html the end marker comes before the start marker")
    line_start = page.rfind("\n", 0, start) + 1
    indent = page[line_start:start]
    if indent.strip():
        raise CheckFailed("The start marker must sit on a line of its own in index.html")
    return start + len(START), end, indent


def shown_issue_number(card_html):
    """The issue number the card shows now, or None for an empty card.
    It's read from the card's meta line only, so the words "Issue 100"
    in a definition can't be mistaken for it."""
    match = re.search(r'<p class="card-meta">Issue (\d+)', card_html)
    return int(match.group(1)) if match else None


def write_atomically(path, text):
    """Save the page in one step: write a temporary file next to it,
    give it the page's permissions, then swap it into place. The page
    is either all old or all new, never half-written."""
    mode = path.stat().st_mode & 0o7777
    handle, temp = tempfile.mkstemp(dir=path.parent, prefix=".latest-issue-", suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="") as out:
            out.write(text)
        os.chmod(temp, mode)
        os.replace(temp, path)
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise


def write_github_outputs(**values):
    """When running in GitHub Actions, hand results to the next step
    through the $GITHUB_OUTPUT file. Every value has been checked by
    now, so none can contain a line break."""
    target = os.environ.get("GITHUB_OUTPUT")
    if not target:
        return
    with open(target, "a", encoding="utf-8") as out:
        for key, value in values.items():
            out.write(f"{key}={value}\n")


def main():
    """Run the whole update, top to bottom. Every check happens before
    index.html is touched; the first one that fails stops the run with
    a message saying what was wrong."""
    args = parse_args()
    page_path = Path(args.page)
    try:
        try:
            with open(page_path, encoding="utf-8", newline="") as source:
                page = source.read()
        except OSError as error:
            raise CheckFailed(f"Couldn't read {page_path}: {error.strerror}")
        inner_start, inner_end, indent = find_card_region(page)

        post = read_newest_post(fetch(args.feed, "feed"))
        filenames = list_issue_files(fetch(args.issues, "list of issue files"))
        number = find_issue_number(post["word"], filenames)

        shown = shown_issue_number(page[inner_start:inner_end])
        if shown is not None and number < shown:
            raise CheckFailed(f"The feed's newest post is Issue {number:03d}, older than "
                              f"Issue {shown:03d} already on the page")

        issue = dict(post, number=number, date=london_date(post["published"]))
        card = build_card(issue, indent)
        new_page = page[:inner_start] + "\n" + card + "\n" + indent + page[inner_end:]
    except CheckFailed as problem:
        print(f"Latest-issue card not changed: {problem}", file=sys.stderr)
        return problem.exit_code

    summary = f"Issue {number:03d}, {issue['word']}, {format_card_date(issue['date'])}"
    if args.dry_run:
        print(card)
        state = "already current" if new_page == page else "would update"
        print(f"\nDry run ({state}): {summary}. index.html not changed.")
        return 0
    if new_page == page:
        print(f"Already current: {summary}")
        write_github_outputs(status="current")
        return 0

    write_atomically(page_path, new_page)
    print(f"Updated the card: {summary}")
    write_github_outputs(status="updated", word=issue["word"], number=f"{number:03d}",
                         card_id=hashlib.sha1(card.encode("utf-8")).hexdigest()[:8],
                         link=issue["link"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
