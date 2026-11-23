
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def get_supabase_config():
    env_path = Path(__file__).parent / ".env"

    config = {}

    with open(env_path, "r", encoding="utf-8") as file:
        for line in file:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                config[key] = value

    return config


def get_jobs():
    config = get_supabase_config()

    url = config["SUPABASE_URL"] + "/rest/v1/jobs?select=*"
    key = config["SUPABASE_KEY"]

    request = Request(
        url,
        headers={
            "apikey": key
        }
    )

    try:
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))

    except HTTPError as error:
        details = error.read().decode("utf-8")
        raise Exception(details)
