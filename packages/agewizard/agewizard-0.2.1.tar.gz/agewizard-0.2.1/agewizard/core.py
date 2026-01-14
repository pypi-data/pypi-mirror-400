from datetime import date, datetime
import re

def _parse_dob(dob: str, date_format: str = None) -> date:
    """Internal helper to parse and normalize DOB with strict validation."""
    if not dob or not isinstance(dob, str):
        raise ValueError("DOB must be a non-empty string.")
    
    # Normalize separators for the input string
    normalized = re.sub(r"[./ ]", "-", dob.strip())
    
    if date_format:
        # Map human-readable patterns to strptime codes
        mapping = {
            "YYYY": "%Y", "YY": "%y",
            "MM": "%m", "DD": "%d"
        }
        fmt_normalized = re.sub(r"[./ ]", "-", date_format.strip())
        for key, val in mapping.items():
            fmt_normalized = fmt_normalized.replace(key, val)
            
        try:
            return datetime.strptime(normalized, fmt_normalized).date()
        except ValueError as e:
            raise ValueError(f"Date '{dob}' does not match format '{date_format}': {e}")
    
    # Automatic generic detection if no format is provided
    # 1. Check for YYYY-MM-DD (Standard)
    if re.match(r"^\d{4}-\d{2}-\d{2}$", normalized):
        y, m, d = map(int, normalized.split("-"))
    # 2. Check for DD-MM-YYYY (Common)
    elif re.match(r"^\d{2}-\d{2}-\d{4}$", normalized):
        d, m, y = map(int, normalized.split("-"))
    else:
        raise ValueError(f"Could not automatically parse '{dob}'. Please specify date_format (e.g., 'YYYY-MM-DD').")

    try:
        return date(y, m, d)
    except ValueError as e:
        raise ValueError(f"Invalid date components in '{dob}': {e}")

def calculate_age(dob: str, date_format: str = None) -> int:
    birth = _parse_dob(dob, date_format)
    today = date.today()
    if birth > today:
        raise ValueError("Date of birth cannot be in the future.")
    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age

def age_in_days(dob: str, date_format: str = None) -> int:
    return (date.today() - _parse_dob(dob, date_format)).days

def age_in_weeks(dob: str, date_format: str = None) -> int:
    return age_in_days(dob, date_format) // 7

def age_in_months(dob: str, date_format: str = None) -> int:
    birth = _parse_dob(dob, date_format)
    today = date.today()
    return (today.year - birth.year) * 12 + today.month - birth.month

def days_until_birthday(dob: str, date_format: str = None) -> int:
    birth = _parse_dob(dob, date_format)
    today = date.today()
    try:
        next_bday = date(today.year, birth.month, birth.day)
    except ValueError:
        next_bday = date(today.year, 3, 1)
    if next_bday < today:
        try:
            next_bday = date(today.year + 1, birth.month, birth.day)
        except ValueError:
            next_bday = date(today.year + 1, 3, 1)
    return (next_bday - today).days

def next_birthday_weekday(dob: str, date_format: str = None) -> str:
    birth = _parse_dob(dob, date_format)
    today = date.today()
    try:
        next_bday = date(today.year, birth.month, birth.day)
    except ValueError:
        next_bday = date(today.year, 3, 1)
    if next_bday < today:
        try:
            next_bday = date(today.year + 1, birth.month, birth.day)
        except ValueError:
            next_bday = date(today.year + 1, 3, 1)
    return next_bday.strftime("%A")

def zodiac_sign(dob: str, date_format: str = None) -> str:
    birth = _parse_dob(dob, date_format)
    m, d = birth.month, birth.day
    if (m == 3 and d >= 21) or (m == 4 and d <= 19): return "Aries"
    if (m == 4 and d >= 20) or (m == 5 and d <= 20): return "Taurus"
    if (m == 5 and d >= 21) or (m == 6 and d <= 20): return "Gemini"
    if (m == 6 and d >= 21) or (m == 7 and d <= 22): return "Cancer"
    if (m == 7 and d >= 23) or (m == 8 and d <= 22): return "Leo"
    if (m == 8 and d >= 23) or (m == 9 and d <= 22): return "Virgo"
    if (m == 9 and d >= 23) or (m == 10 and d <= 22): return "Libra"
    if (m == 10 and d >= 23) or (m == 11 and d <= 21): return "Scorpio"
    if (m == 11 and d >= 22) or (m == 12 and d <= 21): return "Sagittarius"
    if (m == 12 and d >= 22) or (m == 1 and d <= 19): return "Capricorn"
    if (m == 1 and d >= 20) or (m == 2 and d <= 18): return "Aquarius"
    return "Pisces"

def is_leap_year(year_or_dob: object, date_format: str = None) -> bool:
    if isinstance(year_or_dob, str):
        year = _parse_dob(year_or_dob, date_format).year
    else:
        year = int(year_or_dob)
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def is_valid_age(dob: str, date_format: str = None) -> bool:
    try:
        age = calculate_age(dob, date_format)
        return 0 <= age <= 150
    except Exception:
        return False

def is_birthday(dob: str, date_format: str = None) -> bool:
    birth = _parse_dob(dob, date_format)
    today = date.today()
    return birth.month == today.month and birth.day == today.day

def compare_ages(dob1: str, dob2: str, date_format: str = None) -> str:
    d1, d2 = _parse_dob(dob1, date_format), _parse_dob(dob2, date_format)
    diff = abs((d1 - d2).days)
    years = diff // 365
    if d1 < d2:
        return f"Person 1 is older by approx {years} years ({diff} days)."
    elif d1 > d2:
        return f"Person 2 is older by approx {years} years ({diff} days)."
    return "They are the same age."

def human_readable(dob: str, date_format: str = None) -> str:
    birth = _parse_dob(dob, date_format)
    today = date.today()
    years = today.year - birth.year
    months = today.month - birth.month
    days = today.day - birth.day
    if days < 0:
        months -= 1
        days += 30
    if months < 0:
        years -= 1
        months += 12
    return f"{years} years, {months} months, {days} days"

def classify_age(dob: str, date_format: str = None) -> str:
    age = calculate_age(dob, date_format)
    if age <= 2: return "Infant"
    if age <= 12: return "Child"
    if age <= 19: return "Teen"
    if age <= 64: return "Adult"
    return "Senior"

def age_hijri(dob: str, date_format: str = None) -> int:
    days = age_in_days(dob, date_format)
    return int(days / 354.36)

ac = calculate_age

class Age:
    def __init__(self, dob: str, date_format: str = None):
        self.dob = dob
        self.date_format = date_format
        self.birth_date = _parse_dob(dob, date_format)
        self.years = calculate_age(dob, date_format)
        self.days = age_in_days(dob, date_format)
        self.weeks = age_in_weeks(dob, date_format)
        self.months = age_in_months(dob, date_format)
        self.zodiac = zodiac_sign(dob, date_format)
        self.leap_year = is_leap_year(dob, date_format)
        self.next_birthday_days = days_until_birthday(dob, date_format)
        self.next_birthday_weekday = next_birthday_weekday(dob, date_format)
        self.readable = human_readable(dob, date_format)
        self.category = classify_age(dob, date_format)
        self.is_today = is_birthday(dob, date_format)
        self.hijri_age = age_hijri(dob, date_format)

    def is_adult(self, min_age: int = 18) -> bool:
        return self.years >= min_age

    def is_over(self, age: int) -> bool:
        return self.years > age

    def __str__(self): return f"{self.years} years"
    def __int__(self): return self.years
