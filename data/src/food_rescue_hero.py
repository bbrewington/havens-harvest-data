import requests
import pandas as pd

from bs4 import BeautifulSoup

from utility import calculate_date_range, get_env_vars

import io
from argparse import ArgumentParser
from pathlib import Path

def get_rescues_report(username, password, from_date, to_date):
    with requests.Session() as s:
        r = s.get("https://admin.foodrescuehero.org/user_session")
        soup = BeautifulSoup(r.text, features="html.parser")
        authenticity_token = soup.find(id="new_user").css.select('input[name="authenticity_token"]')[0]["value"]
        
        s.post("https://admin.foodrescuehero.org/user_session", {
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
    
    # Use io.StringIO to handle CSV contents as a string
    csv_data = io.StringIO(csv_contents)
    
    # Read CSV contents into a DataFrame
    df = pd.read_csv(csv_data)
    
    # Add the filename as a column
    df["filename"] = Path(dest_file_path).name
    
    # Write DataFrame back to file
    df.to_csv(dest_file_path, index=False, encoding="utf-8")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--dest-file-path")
    parser.add_argument("--days", type=int, default=90, help="Number of days for the date range (default: 90)")
    args = parser.parse_args()

    from_date, to_date, from_date_yyyymmdd, to_date_yyyymmdd = calculate_date_range(type="year_to_date")

    username, password = get_env_vars()
    csv_contents = get_rescues_report(username=username, password=password, from_date=from_date, to_date=to_date)
    dest_file_path = f"{args.dest_file_path}_{from_date_yyyymmdd}_{to_date_yyyymmdd}.csv"
    write_to_file(dest_file_path=dest_file_path, csv_contents=csv_contents)
