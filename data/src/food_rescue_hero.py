import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import urllib

FROM_DATE = urllib.parse.quote("09/28/2024", safe="")
TO_DATE = urllib.parse.quote("12/27/2024", safe="")

load_dotenv()
username = os.getenv("FOOD_RESCUE_HERO_USERNAME")
password = os.getenv("FOOD_RESCUE_HERO_PASSWORD")
assert username and password, "One of Food Rescue Hero username or password env vars are empty"

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
    
    rescues = s.get(f"https://admin.foodrescuehero.org/rescues/report?rescue_date_range={FROM_DATE}+-+{TO_DATE}&format=csv&button=")

with open("rescues.csv", "w", encoding="utf-8") as f:
    f.write(rescues.text)
