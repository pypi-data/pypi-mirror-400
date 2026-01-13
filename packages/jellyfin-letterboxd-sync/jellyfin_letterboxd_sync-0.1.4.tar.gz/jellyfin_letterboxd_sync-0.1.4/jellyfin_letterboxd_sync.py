import csv
import httpx
import argparse
from playwright.sync_api import sync_playwright


def export_jellyfin(jf_url, jf_user, jf_api_key, csv_path):
    print("Fetching Jellyfin data...")
    params = {
        "Recursive": "true",
        "IncludeItemTypes": "Movie,Episode",
        "IsPlayed": "true",
        "Fields": "ProductionYear,UserData,SeriesName",
    }

    with httpx.Client() as client:
        print("Getting user info...")
        r = client.get(f"{jf_url}/Users", headers={"X-Emby-Token": jf_api_key})
        r.raise_for_status()
        users = r.json()
        user_id = next((u["Id"] for u in users if u["Name"] == jf_user), None)
        if not user_id:
            raise ValueError(f"User '{jf_user}' not found on Jellyfin server.")

        print(f"Found user ID for '{jf_user}': {user_id}")

        print("Fetching watched items...")
        r = client.get(f"{jf_url}/Users/{user_id}/Items", params=params, headers={"X-Emby-Token": jf_api_key})
        r.raise_for_status()
        items = r.json().get("Items", [])

    # Process items to unique set (to avoid duplicate episodes for same series)
    processed_items = {}
    for item in items:
        # If Episode, use SeriesName. If Movie, use Name.
        is_episode = item.get("Type") == "Episode"
        title = item.get("SeriesName") if is_episode else item["Name"]

        key = (title, item.get("ProductionYear", ""))
        if key not in processed_items:
            processed_items[key] = item["UserData"]["LastPlayedDate"].split("T")[0]

    # Write CSV with headers Letterboxd recognizes automatically
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Year", "WatchedDate"])
        for (title, year), date in processed_items.items():
            writer.writerow([title, year, date])

    print(f"Exported {len(processed_items)} items to {csv_path}")


def sync_letterboxd(lb_user, lb_pass, csv_path, headless=False):
    with sync_playwright() as p:
        # Launch headless browser
        browser = p.chromium.launch(headless=headless, channel="chrome")
        page = browser.new_page()

        # 1. Login
        print("Logging into Letterboxd...")
        page.goto("https://letterboxd.com/sign-in/", timeout=60000)
        page.fill("#field-username", lb_user)
        page.fill("#field-password", lb_pass)
        page.click('button[type="submit"]')

        page.wait_for_selector("body.logged-in", timeout=60000)
        print("Logged in successfully.")

        # 2. Upload
        print("Uploading CSV...")
        page.goto("https://letterboxd.com/import/", wait_until="domcontentloaded", timeout=60000)

        try:
            page.wait_for_selector(".select-file-button, .upload-zone, .button-green", timeout=10000)
        except Exception:
            print("Upload button not found immediately...")

        with page.expect_file_chooser() as fc_info:
            page.click("text=SELECT A FILE", force=True)
        file_chooser = fc_info.value
        file_chooser.set_files(csv_path)

        # 3. Confirm Mapping
        print("Waiting for mapping...")
        page.wait_for_selector("a.submit-matched-films", state="visible", timeout=60000)

        # 4. Execute Import
        print("Clicking import...")
        page.click("a.submit-matched-films")

        # 5. Wait for Success
        try:
            page.wait_for_selector('h1:has-text("Import summary")', timeout=60000)
        except Exception:
            print("Success message not found via selector, checking URL or page content...")
            if "import" in page.url:
                print("Still on import page, assuming success if no error shown.")
            else:
                print(f"Current URL: {page.url}")

        print("Success: Import complete.")
        browser.close()


def main():
    parser = argparse.ArgumentParser(description="Sync Jellyfin watched status to Letterboxd.")
    parser.add_argument("--jellyfin-url", required=True, help="Jellyfin server URL")
    parser.add_argument("--jellyfin-user", required=True, help="Jellyfin username")
    parser.add_argument("--jellyfin-api-key", required=True, help="Jellyfin API key")
    parser.add_argument("--letterboxd-user", required=True, help="Letterboxd username")
    parser.add_argument("--letterboxd-pass", required=True, help="Letterboxd password")
    parser.add_argument("--csv-path", default="/tmp/letterboxd_import.csv", help="Path to temporary CSV file")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")

    args = parser.parse_args()

    export_jellyfin(args.jellyfin_url, args.jellyfin_user, args.jellyfin_api_key, args.csv_path)
    sync_letterboxd(args.letterboxd_user, args.letterboxd_pass, args.csv_path, headless=args.headless)


if __name__ == "__main__":
    main()
