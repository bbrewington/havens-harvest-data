import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import urllib
from argparse import ArgumentParser
from pathlib import Path
from datetime import datetime, timedelta

def get_env_vars():
    load_dotenv()
    username = os.getenv("FOOD_RESCUE_HERO_USERNAME")
    password = os.getenv("FOOD_RESCUE_HERO_PASSWORD")
    assert username and password, "One of Food Rescue Hero username or password env vars are empty"
    return username, password

def calculate_date_range(days):
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)
    return (
        urllib.parse.quote(from_date.strftime("%m/%d/%Y"), safe=""),
        urllib.parse.quote(to_date.strftime("%m/%d/%Y"), safe=""),
        from_date.strftime("%Y%m%d"),
        to_date.strftime("%Y%m%d")
    )

def get_rescues_report(username, password, from_date, to_date):
    with requests.Session() as s:
        # Get login page (for authenticity token)
        r = s.get("https://admin.foodrescuehero.org/user_session")
        soup = BeautifulSoup(r.text, features="html.parser")
        authenticity_token = soup.find(id="new_user").css.select('input[name="authenticity_token"]')[0]["value"]
        
        # Login
        login = s.post("https://admin.foodrescuehero.org/user_session", {
            "authenticity_token": authenticity_token,
            "user[phone_or_email]": username,
            "user[password]": password,
            "commit": "Login"
        })
        
        rescues = s.get(f"https://admin.foodrescuehero.org/rescues/report?rescue_date_range={from_date}+-+{to_date}&format=csv&button=")
        rescues.raise_for_status()
    
    return rescues.text

def write_to_file(dest_file_path, csv_contents):
    Path(dest_file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(dest_file_path, "w", encoding="utf-8") as f:
        f.write(csv_contents)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--dest-file-path")
    parser.add_argument("--days", type=int, default=90, help="Number of days for the date range (default: 90)")
    args = parser.parse_args()

    from_date, to_date, from_date_yyyymmdd, to_date_yyyymmdd = calculate_date_range(args.days)

    username, password = get_env_vars()
    csv_contents = get_rescues_report(username=username, password=password, from_date=from_date, to_date=to_date)
    dest_file_path = f"{args.dest_file_path}_{from_date_yyyymmdd}_{to_date_yyyymmdd}"
    write_to_file(dest_file_path=dest_file_path, csv_contents=csv_contents)
