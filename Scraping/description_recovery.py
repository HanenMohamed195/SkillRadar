
import json
import math
import os
import re
import time
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "jobspy_jobs.json"
TEMP_FILE = BASE_DIR / "data" / "jobspy_jobs.tmp"

REQUEST_DELAY = 4
MIN_DESCRIPTION_LENGTH = 150

MISSING_VALUES = {
    "", "nan", "none", "null", "n/a", "na",
    "not available", "not provided", "undefined"
}


def is_missing(value):
    if value is None:
        return True
    return str(value).strip().lower() in MISSING_VALUES


def clean_text(value):
    if not value:
        return ""

    soup = BeautifulSoup(str(value), "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    return re.sub(
        r"\s+", " ", soup.get_text(" ", strip=True)
    ).strip()


def extract_json_ld_description(soup):
    for script in soup.find_all(
        "script", type="application/ld+json"
    ):
        try:
            data = json.loads(
                script.string or script.get_text()
            )

            items = data if isinstance(data, list) else [data]

            for item in items:
                if not isinstance(item, dict):
                    continue

                candidates = [item]

                graph = item.get("@graph", [])
                if isinstance(graph, list):
                    candidates.extend(graph)

                for entry in candidates:
                    if not isinstance(entry, dict):
                        continue

                    job_type = entry.get("@type", [])
                    if isinstance(job_type, str):
                        job_type = [job_type]

                    if "JobPosting" not in job_type:
                        continue

                    description = clean_text(
                        entry.get("description")
                    )

                    if len(description) >= MIN_DESCRIPTION_LENGTH:
                        return description

        except (json.JSONDecodeError, TypeError):
            continue

    return ""


def extract_page_description(soup):
    selectors = [
        "[data-automation='jobDescription']",
        "#jobDescription",
        ".job-description",
        "[class*='jobDescription']",
        "[class*='job-description']",
    ]

    for selector in selectors:
        for element in soup.select(selector):
            description = clean_text(element.get_text())

            if len(description) >= MIN_DESCRIPTION_LENGTH:
                return description

    for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
        heading_text = clean_text(
            heading.get_text()
        ).lower()

        if heading_text in {"job description", "description"}:
            parent = heading.parent

            if parent:
                description = clean_text(parent.get_text())
                description = re.sub(
                    r"^(job description|description)\s*",
                    "",
                    description,
                    flags=re.IGNORECASE
                )

                if len(description) >= MIN_DESCRIPTION_LENGTH:
                    return description

    return ""


def recover_description(url):
    parsed = urlparse(str(url))

    if parsed.scheme not in {"http", "https"}:
        return None, "invalid_url"

    if not (
        parsed.hostname == "bayt.com"
        or (
            parsed.hostname
            and parsed.hostname.endswith(".bayt.com")
        )
    ):
        return None, "not_a_bayt_url"

    headers = {
        "User-Agent": "SkillRadar-DescriptionResearch/1.0"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=20,
            allow_redirects=True
        )

        if response.status_code in {401, 403, 429}:
            return None, f"access_restricted_{response.status_code}"

        if response.status_code != 200:
            return None, f"http_{response.status_code}"

        soup = BeautifulSoup(response.text, "html.parser")

        description = extract_json_ld_description(soup)

        if description:
            return description, "recovered_json_ld"

        description = extract_page_description(soup)

        if description:
            return description, "recovered_html"

        return None, "description_not_found"

    except requests.Timeout:
        return None, "timeout"

    except requests.RequestException as error:
        return None, f"request_error: {type(error).__name__}"


def save_jobs(jobs):
    with open(TEMP_FILE, "w", encoding="utf-8") as file:
        json.dump(
            jobs,
            file,
            ensure_ascii=False,
            indent=4,
            allow_nan=False
        )

    os.replace(TEMP_FILE, INPUT_FILE)


def main():
    if not INPUT_FILE.exists():
        print(f"File not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        jobs = json.load(file)

    if not isinstance(jobs, list):
        print("Invalid format: expected a JSON list.")
        return

    pending = []

    for index, job in enumerate(jobs):
        source = str(job.get("source") or "").strip().lower()

        if source != "bayt":
            continue

        if not is_missing(job.get("description")):
            continue

        if job.get("description_recovery_status") == "failed":
            continue

        pending.append((index, job))

    print(f"Total jobs: {len(jobs)}")
    print(f"Bayt jobs to process: {len(pending)}")

    recovered = 0
    failed = 0

    for number, (index, job) in enumerate(pending, start=1):
        print(
            f"\n[{number}/{len(pending)}] "
            f"{job.get('title')}"
        )

        url = job.get("job_url")

        if is_missing(url):
            description = None
            status = "missing_job_url"
        else:
            description, status = recover_description(url)

        job["description_recovery_status"] = (
            "recovered" if description else "failed"
        )

        job["description_recovery_attempted_at"] = (
            datetime.now(timezone.utc).isoformat()
        )

        if description:
            job["description"] = description
            job["description_recovery_source"] = str(url)
            recovered += 1
            print(f"Recovered: {len(description)} characters")
        else:
            failed += 1
            job["description_recovery_error"] = status
            print(f"Not recovered: {status}")

        # Save after every job so progress is preserved
        save_jobs(jobs)

        print("Progress saved.")

        if number < len(pending):
            time.sleep(REQUEST_DELAY)

    print("\n========== RECOVERY SUMMARY ==========")
    print(f"Processed: {len(pending)}")
    print(f"Recovered: {recovered}")
    print(f"Not recovered: {failed}")
    print(f"Updated file: {INPUT_FILE}")


if __name__ == "__main__":
    main()
