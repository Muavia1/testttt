"""
Browser automation using HyperBrowser (Browser Use agent + Scrape API).

- Without profile: Browser Use task = login at TARGET_URL + optional steps.
- With profile: Scrape TARGET_URL1 with the profile (logged-in session), save full page
  content to files for later planning of what to properly scrape.

Usage:
  python facebook_browser.py              # Start task (non-blocking) or run scrape
  python facebook_browser.py --wait       # Wait for task (no-profile) or run scrape (profile)

.env:
  HYPERBROWSER_API_KEY (required)
  TARGET_URL (login page; default: https://www.entreaseai.com/)
  TARGET_URL1 (page to scrape when profile set; default: Facebook Marketplace vehicles)
  LOGIN_EMAIL or FACEBOOK_EMAIL, LOGIN_PASSWORD or FACEBOOK_PASSWORD (when no profile)
  HYPERBROWSER_FACEBOOK_PROFILE_ID or PROFILE_ID (optional; leave empty for first run)
  SCRAPE_OUTPUT_DIR (optional; directory to save scrape files; default: current directory)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from hyperbrowser import Hyperbrowser
from hyperbrowser.models import (
    CreateProfileParams,
    CreateSessionParams,
    CreateSessionProfile,
    StartBrowserUseTaskParams,
    StartScrapeJobParams,
)

try:
    from hyperbrowser.models import ScrapeOptions
except ImportError:
    ScrapeOptions = None

load_dotenv()

PROFILE_ID = (
    os.getenv("HYPERBROWSER_FACEBOOK_PROFILE_ID") or os.getenv("PROFILE_ID") or ""
).strip()

EMAIL = (
    os.getenv("LOGIN_EMAIL") or os.getenv("FACEBOOK_EMAIL") or ""
).strip()
PASSWORD = (
    os.getenv("LOGIN_PASSWORD") or os.getenv("FACEBOOK_PASSWORD") or ""
).strip()
TARGET_URL = os.getenv("TARGET_URL", "https://www.entreaseai.com/").strip()
TARGET_URL1 = os.getenv("TARGET_URL1", "https://www.facebook.com/marketplace/category/vehicles?sortBy=creation_time_descend&topLevelVehicleType=car_truck&exact=false").strip()
HYPERBROWSER_API_KEY = os.getenv("HYPERBROWSER_API_KEY", "").strip()
SCRAPE_OUTPUT_DIR = os.getenv("SCRAPE_OUTPUT_DIR", ".").strip()

# Optional JSON array of extra steps, e.g. STEPS='["Go to dashboard", "Open settings"]'
STEPS_JSON = os.getenv("STEPS", "[]").strip()


def parse_steps():
    try:
        steps = json.loads(STEPS_JSON)
        return steps if isinstance(steps, list) else []
    except json.JSONDecodeError:
        return []


def build_task(steps: list[str], use_login: bool) -> str:
    if use_login:
        task = f"""1. Navigate to {TARGET_URL}
2. Wait for the page to load completely
3. Look for a login form or sign-in button
4. If you see a login form, enter the following credentials:
   - Email: {EMAIL}
   - Password: {PASSWORD}
5. Click the login/sign-in button
6. Wait for the login process to complete
8. After clicking login button wait for 4 minutes then close.
"""
        step_start = 9
    else:
        # With profile: just go to target URL, wait 1 minute, then close
        task = f"""1. Navigate to {TARGET_URL1}
2. Wait for the page to load completely (you are already logged in).
3. Wait 1 minute (60 seconds).
4. Report success; the session will then close.
"""
        return task

    if steps:
        for i, step in enumerate(steps, start=step_start):
            task += f"{i}. {step}\n"
        next_num = step_start + len(steps)
    else:
        task += f"{step_start}. Navigate to the dashboard\n"
        next_num = step_start + 1

    task += f"""
{next_num}. Report the final status: success or failure with details but do not show password.
{next_num + 1}. If any step fails, note the specific error and continue with remaining steps if possible.
"""
    return task


def get_client():
    if not HYPERBROWSER_API_KEY:
        print("Error: HYPERBROWSER_API_KEY is not set in .env")
        sys.exit(1)
    return Hyperbrowser(api_key=HYPERBROWSER_API_KEY)


def run_scrape_and_save(client: Hyperbrowser):
    """When user has profile: scrape TARGET_URL1 with that profile and save full page to files."""
    session_options = CreateSessionParams(
        profile=CreateSessionProfile(id=PROFILE_ID, persist_changes=False),
    )
    scrape_options_kw = {
        "only_main_content": False,
        "formats": ["markdown", "html"],
    }
    scrape_params_kw = {
        "url": TARGET_URL1,
        "session_options": session_options,
    }
    if ScrapeOptions is not None:
        scrape_params_kw["scrape_options"] = ScrapeOptions(**scrape_options_kw)
    else:
        scrape_params_kw["scrape_options"] = scrape_options_kw

    print(f"Scraping {TARGET_URL1} with profile (logged-in session)...")
    result = client.scrape.start_and_wait(params=StartScrapeJobParams(**scrape_params_kw))

    if result.status != "completed":
        print(f"Scrape failed: {result.status}", getattr(result, "error", ""))
        return

    data = getattr(result, "data", None)
    if not data:
        print("No scrape data in response.")
        return

    out_dir = Path(SCRAPE_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = out_dir / f"scrape_{ts}"

    saved = []
    if getattr(data, "markdown", None):
        path = base.with_suffix(".md")
        path.write_text(data.markdown, encoding="utf-8")
        saved.append(str(path))
    if getattr(data, "html", None):
        path = base.with_name(base.name + "_html").with_suffix(".html")
        path.write_text(data.html, encoding="utf-8")
        saved.append(str(path))
    if getattr(data, "metadata", None):
        meta_path = base.with_name(base.name + "_metadata").with_suffix(".json")
        meta = data.metadata
        if hasattr(meta, "model_dump"):
            meta = meta.model_dump()
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        saved.append(str(meta_path))

    if saved:
        print("Saved full page content to:")
        for p in saved:
            print(f"  {p}")
        print("You can use these to plan what to properly scrape next.")
    else:
        print("No markdown or html in response; check API response.")


def run_task(client: Hyperbrowser, wait: bool):
    if PROFILE_ID:
        run_scrape_and_save(client)
        return

    steps = parse_steps()
    use_login = True
    if not EMAIL or not PASSWORD:
        print("Error: LOGIN_EMAIL (or FACEBOOK_EMAIL) and LOGIN_PASSWORD (or FACEBOOK_PASSWORD) must be set in .env when PROFILE_ID is empty.")
        sys.exit(1)

    task = build_task(steps, use_login)

    session_id = None
    created_profile_id = None

    # No profile: create one so we can save login state and reuse it next time
    profile = client.profiles.create(
        params=CreateProfileParams(name="browser-use-login-profile")
    )
    created_profile_id = profile.id
    print(f"Created profile: {created_profile_id}")
    session = client.sessions.create(
        params=CreateSessionParams(
            profile=CreateSessionProfile(
                id=created_profile_id,
                persist_changes=True,  # Save cookies/login when session ends
            ),
        )
    )
    session_id = session.id

    kwargs = {
        "task": task,
        "max_steps": 40,
        "session_id": session_id,
    }
    if use_login:
        kwargs["mask_inputs"] = {"x_user": EMAIL, "x_pass": PASSWORD}

    params = StartBrowserUseTaskParams(**{k: v for k, v in kwargs.items() if v is not None})

    if wait:
        result = client.agents.browser_use.start_and_wait(params=params)
        print("Status:", result.status)
        if getattr(result, "data", None) and getattr(result.data, "final_result", None):
            print("Result:\n", result.data.final_result)
        if session_id:
            client.sessions.stop(session_id)
        if created_profile_id:
            _print_save_profile_instructions(created_profile_id)
        return

    started = client.agents.browser_use.start(params=params)
    print("Task started (non-blocking)")
    print("Job ID:", getattr(started, "job_id", None))
    if getattr(started, "live_url", None):
        print("Watch live:", started.live_url)
    if created_profile_id:
        _print_save_profile_instructions(created_profile_id)


def _print_save_profile_instructions(profile_id: str):
    """Print how to save the profile ID so the user can reuse it and skip login next time."""
    print()
    print("Save this profile ID in your .env to reuse it next time (login once):")
    print(f'HYPERBROWSER_FACEBOOK_PROFILE_ID="{profile_id}"')
    print("(Profile is saved when the task finishes and the session closes.)")


def main():
    parser = argparse.ArgumentParser(description="Run Browser Use task (login + optional steps)")
    parser.add_argument("--wait", action="store_true", help="Wait for task to complete and print result")
    args = parser.parse_args()

    client = get_client()
    run_task(client, wait=args.wait)


if __name__ == "__main__":
    main()
