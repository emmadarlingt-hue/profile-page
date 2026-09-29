#!/usr/bin/env python3
"""Rewrite the "Latest issue" card in index.html from promptwrought-site.

Run by .github/workflows/latest-issue.yml on Tuesdays, or by hand:

    python3 tools/update-latest-issue.py            # update index.html
    python3 tools/update-latest-issue.py --dry-run  # show the card, change nothing

It reads the issue files in the promptwrought-site repo (issues/NNN-word.json),
takes the highest-numbered one whose release moment has passed, and replaces
only what sits between the latest-issue start and end markers in index.html.
If anything is missing or looks wrong it changes nothing, says what the
problem is and exits with an error: a half-filled card is never written.

Why not the Substack feed: Substack answers GitHub's runners with HTTP 403
(found 29 Sep 2026), so the feed can't be read from the Action at all.

Exit codes:
    0   the card was updated, or was already current
    1   a check failed, so nothing was changed
    75  an issue went out less than a day ago but its file isn't on
        promptwrought-site's main yet: try again later. (75 is the usual
        "temporary failure" code, and it can't be mistaken for Python's own
        errors, which use 1 and 2.)

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
from datetime import date, datetime, timedelta, time as clock_time
from pathlib import Path
from zoneinfo import ZoneInfo

# ---------- Where things live ----------
ISSUES_URL = "https://api.github.com/repos/emmadarlingt-hue/promptwrought-site/contents/issues"
REF = "main"                               # read the issue files as they are on main
POST_HOST = "promptwrought.substack.com"   # the only site the card may link to
PAGE = Path(__file__).resolve().parent.parent / "index.html"

# The card lives between these two comments in index.html.
START = "<!-- latest-issue:start -->"
END = "<!-- latest-issue:end -->"

# Issue files are named like "009-verifidget.json": the number, a hyphen,
# the word, ".json". Group 1 is the number, group 2 the word.
ISSUE_FILE = re.compile(r"(\d{3,})-([a-z0-9-]+)\.json")

# ---------- The release calendar ----------
# Copied from promptwrought-site/tools/build-lexicon.py, where the same
# numbers drive its publish guard. Change both together: nothing checks
# that they still agree. Issue 1 is ISO week 31, so issue N is week N + 30,
# and it goes out at 13:31 London time on that week's Tuesday.
VOLUME_YEAR = 2026
FIRST_ISSUE_WEEK = 31
TOTAL_WEEKS = 52                   # the volume stops at week 52
TUESDAY = 2                        # in ISO numbering Monday is 1
RELEASE_TIME = clock_time(13, 31)  # the Substack send, to the minute
LONDON = ZoneInfo("Europe/London")
LAST_ISSUE = TOTAL_WEEKS - FIRST_ISSUE_WEEK + 1   # 22: the volume's last issue

LATE_WINDOW = timedelta(hours=24)  # how long a missing file counts as "late"
MAX_LISTING = 1000                 # GitHub lists at most this many files
MAX_BYTES = 5_000_000              # far more than any issue file needs

# Substack's month style, as the card has always shown it: "22 Sept 2026".
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "June",
          "July", "Aug", "Sept", "Oct", "Nov", "Dec"]


class CheckFailed(Exception):
    """A problem that means the card must not change. Exit code 1."""
    exit_code = 1


class IssueFileMissing(CheckFailed):
    """An issue went out, but its file isn't on promptwrought-site's main
    yet. A later run will try again. Exit code 75."""
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


def warn(message):
    """Say something worth knowing without stopping the run. In GitHub
    Actions it becomes a yellow warning on the run's summary page (the
    ::warning:: line is how a script asks for one); elsewhere it's a
    plain line on stderr."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::warning::{message}")
    else:
        print(f"Warning: {message}", file=sys.stderr)


def parse_args():
    """Read the command-line options. The defaults are promptwrought-site
    on GitHub, the real clock and this repo's index.html; the options exist
    so the checks can be tried on a local folder of test files at any
    pretend time."""
    parser = argparse.ArgumentParser(
        description="Rewrite the Latest issue card in index.html from promptwrought-site.")
    parser.add_argument("--issues", default=ISSUES_URL,
                        help="the issues folder: GitHub's contents API address (default) "
                             "or a local folder, such as a clone of promptwrought-site")
    parser.add_argument("--page", default=str(PAGE),
                        help="the page to update (default: this repo's index.html)")
    parser.add_argument("--now", default=None,
                        help="pretend it's this time, e.g. 2026-10-06T13:31 (London time "
                             "unless a zone is given); for testing")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the card and change nothing")
    return parser.parse_args()


def parse_now(text):
    """The moment to judge releases by: the real time, or --now for
    tests. A time without a zone is read as London time. A trailing Z
    (UTC) is accepted too, even on Python 3.9, which can't read one by
    itself."""
    if text is None:
        return datetime.now(LONDON)
    cleaned = text.strip()
    if cleaned[-1:] in ("Z", "z"):
        cleaned = cleaned[:-1] + "+00:00"
    try:
        when = datetime.fromisoformat(cleaned)
    except ValueError:
        raise CheckFailed(f"--now {text!r} isn't a date and time like 2026-10-06T13:31")
    return when if when.tzinfo else when.replace(tzinfo=LONDON)


def fetch(source, what, accept="application/vnd.github+json"):
    """Download an address (or read a local file) and return its bytes.
    It tries three times, a few seconds apart, because a runner's first
    request can fail for reasons that have nothing to do with us. The
    GitHub token, when there is one, is only ever sent to GitHub's API,
    and it is never printed."""
    if "://" not in source:  # a plain file path: a local folder or a test
        try:
            return Path(source).read_bytes()
        except OSError as error:
            raise CheckFailed(f"Couldn't read the {what} from {source}: {error.strerror}")

    headers = {"User-Agent": "emmadarling.dev latest-issue updater"}
    if urllib.parse.urlsplit(source).hostname == "api.github.com":
        headers["Accept"] = accept
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


def github_url(source, name=None):
    """The contents-API address for the issues folder, or for one file in
    it, always asking for main, so a change of default branch can't
    change what is read."""
    parts = urllib.parse.urlsplit(source)
    path = parts.path.rstrip("/") + (f"/{urllib.parse.quote(name)}" if name else "")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, f"ref={REF}", ""))


def list_issue_files(source):
    """Return the file names in the issues folder: from GitHub's listing,
    or from a local folder. If GitHub sends something other than a list
    of files (a rate-limit message, say), stop. GitHub lists 1,000 files
    at most, so a listing that long can't be trusted to be complete."""
    if "://" not in source:
        try:
            return sorted(n for n in os.listdir(source) if os.path.isfile(os.path.join(source, n)))
        except OSError as error:
            raise CheckFailed(f"Couldn't read the issues folder {source}: {error.strerror}")

    try:
        entries = json.loads(fetch(github_url(source), "list of issue files"))
    except ValueError:
        raise CheckFailed("GitHub's list of issue files isn't readable JSON")
    if not isinstance(entries, list):
        message = entries.get("message") if isinstance(entries, dict) else None
        raise CheckFailed("GitHub didn't send the list of issue files"
                          + (f": {message}" if message else ""))
    if len(entries) >= MAX_LISTING:
        raise CheckFailed(f"GitHub listed {len(entries)} files, its limit, so the newest "
                          "issue file might be missing from the list")
    return [entry.get("name", "") for entry in entries
            if isinstance(entry, dict) and entry.get("type") == "file"]


def read_issue(source, name):
    """Read one issue file and return its fields. From GitHub it asks
    for the raw file through the API, which is always up to date (the
    raw.githubusercontent.com copy can lag by minutes)."""
    if "://" in source:
        raw = fetch(github_url(source, name), f"issue file {name}",
                    accept="application/vnd.github.raw+json")
    else:
        raw = fetch(os.path.join(source, name), f"issue file {name}")
    try:
        fields = json.loads(raw)
    except ValueError:
        raise CheckFailed(f"{name} isn't readable JSON")
    if not isinstance(fields, dict):
        raise CheckFailed(f"{name} doesn't hold a set of fields (a JSON object)")
    return fields


def release_moment(number):
    """When issue `number` goes out to subscribers: 13:31 London time on
    the Tuesday of ISO week number + 30 of VOLUME_YEAR, as an aware
    datetime. Issue 10 is week 40, so Tuesday 29 Sep 2026 at 13:31.

    Raises CheckFailed if the week falls outside the volume (weeks 1 to
    TOTAL_WEEKS): a second year needs its own VOLUME_YEAR, here and in
    promptwrought-site."""
    week = number + FIRST_ISSUE_WEEK - 1
    if not 1 <= week <= TOTAL_WEEKS:
        raise CheckFailed(f"Issue {number} would fall in week {week}, "
                          f"outside weeks 1-{TOTAL_WEEKS} of {VOLUME_YEAR}")
    day = date.fromisocalendar(VOLUME_YEAR, week, TUESDAY)
    return datetime.combine(day, RELEASE_TIME, tzinfo=LONDON)


def plain_text(value, field, name):
    """A field from an issue file as the plain sentence a reader sees.
    Issue files hold HTML fragments (<em>, &amp;), so, like
    promptwrought-site's own plain(), tags come out and entities turn
    back into characters; runs of spaces and line breaks become single
    spaces. A missing or empty field stops the update, and so does a
    bare "<" that isn't part of a tag: in an HTML fragment that means a
    typo, and guessing would change the sentence. An escaped &lt; is
    fine; it's just a "<" in the text."""
    if not isinstance(value, str):
        raise CheckFailed(f"{name} has no {field} (it's missing, or not text)")
    untagged = re.sub(r"</?[A-Za-z][^<>]*>", "", value)
    if "<" in untagged:
        raise CheckFailed(f"{name}'s {field} has a '<' that isn't part of a tag "
                          f"({value[:60]!r})")
    tidy = " ".join(html.unescape(untagged).split())
    if not tidy:
        raise CheckFailed(f"{name} has an empty {field}")
    return tidy


def check_word(word):
    """The word must start with a letter and use only letters, digits and
    single hyphens (the same characters the issue file names allow),
    because it ends up in a branch name, a pull request title and the
    card's link as well as on the page."""
    if not isinstance(word, str) or not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", word):
        raise CheckFailed(f"The issue's word {word!r} isn't a single coined word "
                          "(lower-case letters, digits and hyphens, starting with a letter)")
    return word


def check_link(url):
    """The card's link must be an https address for a post on the
    newsletter's own Substack. Anything else (plain http, another site,
    a moved domain) stops the update rather than going live. Any query
    or fragment is dropped."""
    parts = urllib.parse.urlsplit(url)
    if (parts.scheme != "https" or parts.hostname != POST_HOST
            or not re.fullmatch(r"/p/[a-z0-9-]+/?", parts.path)):
        raise CheckFailed(f"The link {url!r} isn't an https link to a post on {POST_HOST}")
    return urllib.parse.urlunsplit(("https", POST_HOST, parts.path.rstrip("/"), "", ""))


def find_issue_number(word, filenames):
    """Work out the issue number for a word from the promptwrought-site
    file names, which look like "009-verifidget.json".

    Returns the number as an int (9 for "009-verifidget.json").
    Raises CheckFailed if more than one file matches, because then the
    number would be a guess. Raises IssueFileMissing if none does; since
    the word now comes from a file name, that can't happen here, and the
    call is the check that no other file claims the same word."""
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


def read_checked_issue(source, name, number, filenames, released):
    """Read one issue file and check it against its own file name, field
    by field, then build the card's link from the word. The file's
    issueUrl, when it's filled in, must be a valid post link and the same
    link: it was checked against Substack when the issue was written, and
    the runner can't reach Substack to check it now. (promptwrought-site
    allows it to be empty for a while; then the built link stands alone.)"""
    fields = read_issue(source, name)
    no, word = fields.get("no"), fields.get("word")
    if isinstance(no, bool) or not isinstance(no, int) or no != number:
        raise CheckFailed(f"{name} says it's Nº {no!r}, but its file name says {number:03d}")
    if word != ISSUE_FILE.fullmatch(name).group(2):
        raise CheckFailed(f"{name} holds the word {word!r}, which doesn't match its file name")
    word = check_word(word)
    definition = plain_text(fields.get("definition"), "definition", name)
    if find_issue_number(word, filenames) != number:
        raise CheckFailed(f"The word {word!r} belongs to a different issue file than {name}")

    link = f"https://{POST_HOST}/p/{word}"   # word is already checked: letters, digits, hyphens
    issue_url = fields.get("issueUrl")
    if issue_url is None:
        issue_url = ""
    if not isinstance(issue_url, str):
        raise CheckFailed(f"{name}'s issueUrl isn't text")
    if issue_url.strip() and check_link(issue_url.strip()) != link:
        raise CheckFailed(f"{name}'s issueUrl is {issue_url.strip()!r}, but the card's link "
                          f"would be {link!r}; they must agree")
    return {"number": number, "word": word, "definition": definition,
            "link": link, "date": released.date()}


def choose_issue(source, filenames, now):
    """Pick the issue the card should show: the highest-numbered issue
    file whose release moment has passed. A file that isn't out yet is
    skipped with a warning: it shouldn't be on main before its release,
    so promptwrought-site's publish guard was bypassed. Two files with
    the same number stop the update."""
    by_number = {}
    for name in filenames:
        m = ISSUE_FILE.fullmatch(name)
        if not m:
            continue
        number = int(m.group(1))
        if number in by_number:
            raise CheckFailed(f"Two issue files both claim Nº {number:03d}: "
                              f"{by_number[number]} and {name}")
        by_number[number] = name
    if not by_number:
        raise CheckFailed("There are no issue files (named like 010-word.json) in the issues folder")

    for number in sorted(by_number, reverse=True):
        released = release_moment(number)
        if released > now:
            warn(f"{by_number[number]} is on promptwrought-site's main, but it isn't out until "
                 f"{released:%a %d %b %H:%M} London time, so it was skipped. Its word may already "
                 "be live on promptwrought.com: the publish guard must have been bypassed.")
            continue
        return read_checked_issue(source, by_number[number], number, filenames, released)
    raise CheckFailed("None of the issue files has been released yet")


def check_not_late(chosen, now):
    """If the calendar says a newer issue than the chosen one went out
    less than a day ago, its file should be on main by now: stop with
    exit 75, so the workflow warns (and, on the last catch-up, fails).
    After a day, carry on quietly with the newest file there is: that
    week may have been skipped on purpose."""
    expected = None
    for number in range(1, LAST_ISSUE + 1):
        if release_moment(number) > now:
            break
        expected = number
    if expected is None or expected <= chosen:
        return
    due = release_moment(expected)
    if now - due < LATE_WINDOW:
        raise IssueFileMissing(f"Issue {expected:03d} was due at {due:%H:%M} London time on "
                               f"{due:%a %d %b}, but its file isn't on promptwrought-site's main "
                               "yet. (If that week was skipped on purpose, this stops a day "
                               "after the due time.)")


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
    screen-reader name includes the word. Every value is escaped, so
    text can never turn into HTML.
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
        now = parse_now(args.now)
        try:
            with open(page_path, encoding="utf-8", newline="") as source:
                page = source.read()
        except OSError as error:
            raise CheckFailed(f"Couldn't read {page_path}: {error.strerror}")
        inner_start, inner_end, indent = find_card_region(page)

        filenames = list_issue_files(args.issues)
        issue = choose_issue(args.issues, filenames, now)
        number = issue["number"]

        shown = shown_issue_number(page[inner_start:inner_end])
        if shown is not None and number < shown:
            raise CheckFailed(f"The newest released issue file is Issue {number:03d}, older "
                              f"than Issue {shown:03d} already on the page")
        check_not_late(number, now)

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
