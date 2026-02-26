"""
Browser automation using HyperBrowser Browser Use agent (no Chromium/Playwright).

Builds a task that: navigates to TARGET_URL, finds login form, enters email/password
from .env, clicks login, then runs optional steps and reports status.

- Without profile: full task = login + your steps.
- With profile: creates a session with that profile and runs task in it (already logged in).
- CAPTCHA solving is enabled on the session (solve_captchas=True); may require a paid HyperBrowser plan.

Usage:
  python facebook_browser.py              # Start task (non-blocking), print job_id and live_url
  python facebook_browser.py --wait       # Block until task completes and print result

.env:
  HYPERBROWSER_API_KEY (required)
  TARGET_URL (default: https://www.entreaseai.com/)
  LOGIN_EMAIL or FACEBOOK_EMAIL
  LOGIN_PASSWORD or FACEBOOK_PASSWORD
  HYPERBROWSER_FACEBOOK_PROFILE_ID or PROFILE_ID (optional; leave empty for first run)
  STEPS (optional) JSON array of step strings, e.g. ["Go to dashboard", "Click first item"]
"""

import argparse
import json
import os
import sys
from dotenv import load_dotenv
from hyperbrowser import Hyperbrowser
from hyperbrowser.models import (
    CreateProfileParams,
    CreateSessionParams,
    CreateSessionProfile,
    StartBrowserUseTaskParams,
)

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


def run_task(client: Hyperbrowser, wait: bool):
    steps = parse_steps()
    use_login = not PROFILE_ID
    if use_login and (not EMAIL or not PASSWORD):
        print("Error: LOGIN_EMAIL (or FACEBOOK_EMAIL) and LOGIN_PASSWORD (or FACEBOOK_PASSWORD) must be set in .env when PROFILE_ID is empty.")
        sys.exit(1)

    task = build_task(steps, use_login)

    session_id = None
    session_options = None
    created_profile_id = None

    if PROFILE_ID:
        session = client.sessions.create(
            params=CreateSessionParams(
                profile=CreateSessionProfile(id=PROFILE_ID, persist_changes=False),
                solve_captchas=True,
            )
        )
        session_id = session.id
    else:
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
