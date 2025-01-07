import os
import urllib

from dotenv import load_dotenv

from datetime import datetime, timedelta

def get_env_vars():
    load_dotenv()
    username = os.getenv("FOOD_RESCUE_HERO_USERNAME")
    password = os.getenv("FOOD_RESCUE_HERO_PASSWORD")
    assert username and password, "One of Food Rescue Hero username or password env vars are empty"
    return username, password

def calculate_date_range(type, from_date=None, to_date=None, num_days=None):
    """
    Calculate a date range in different formats based on the specified type.

    Parameters:
    ----------
    type : str
        Specifies the type of date range to calculate. Accepted values are:
        - "days_before_today": Calculates a range starting `num_days` before today and ending today.
        - "dates": Uses specific `from_date` and `to_date` provided as strings in "YYYY-MM-DD" format.
        - "year_to_date": Calculates the range from the start of the current year to yesterday.
    from_date : str, optional
        The start date in "YYYY-MM-DD" format. Required if `type` is "dates".
    to_date : str, optional
        The end date in "YYYY-MM-DD" format. Required if `type` is "dates".
    num_days : int, optional
        The number of days before today to include in the range. Required if `type` is "days_before_today".

    Returns:
    -------
    tuple
        A tuple containing the date range in four formats:
        - `from_date` in "MM/DD/YYYY" format, URL-encoded.
        - `to_date` in "MM/DD/YYYY" format, URL-encoded.
        - `from_date` in "YYYYMMDD" format.
        - `to_date` in "YYYYMMDD" format.

    Raises:
    ------
    AssertionError
        If the required arguments for a specific `type` are not provided.

    Examples:
    --------
    # Example for "days_before_today"
    calculate_date_range("days_before_today", num_days=30)
    # Returns: ('11%2F07%2F2023', '12%2F07%2F2023', '20231107', '20231207')

    # Example for "dates"
    calculate_date_range("dates", from_date="2023-01-01", to_date="2023-12-31")
    # Returns: ('01%2F01%2F2023', '12%2F31%2F2023', '20230101', '20231231')

    # Example for "year_to_date" (if today's date is 2025-01-07)
    calculate_date_range("year_to_date")
    # Returns: ('01%2F01%2F2023', '12%2F06%2F2023', '20230101', '20231206')
    """
    if type == "days_before_today":
        assert num_days, "for date range type 'days_before_today', must provide `num_days`"
        to_date = datetime.now()
        from_date = to_date - timedelta(days=num_days)
    elif type == "dates":
        assert from_date and to_date, "for date range type 'dates', must provide `from_date` & `to_date`"
        from_date = datetime.strptime(from_date, "%Y-%m-%d")
        to_date = datetime.strptime(to_date, "%Y-%m-%d")
    elif type == "year_to_date":
        from_date = datetime.strptime(f"{datetime.today().year}-01-01", "%Y-%m-%d")
        to_date = datetime.today() - timedelta(days=1)
    return (
        urllib.parse.quote(from_date.strftime("%m/%d/%Y"), safe=""),
        urllib.parse.quote(to_date.strftime("%m/%d/%Y"), safe=""),
        from_date.strftime("%Y%m%d"),
        to_date.strftime("%Y%m%d")
    )
