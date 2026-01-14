from datetime import date, timedelta
import re

def _parse_dob(dob: str) -> date:
    """Internal helper to parse and normalize DOB."""
    if not dob or not isinstance(dob, str):
        raise ValueError("DOB must be a non-empty string.")
    normalized = re.sub(r"[./ ]", "-", dob.strip())
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", normalized):
        raise ValueError(f"Invalid format '{dob}'. Use YYYY-MM-DD.")
    y, m, d = map(int, normalized.split("-"))
    # Basic date validation
    return date(y, m, d)

def calculate_age(dob: str) -> int:
    """Returns age in years."""
    birth = _parse_dob(dob)
    today = date.today()
    if birth > today:
        raise ValueError("Date of birth cannot be in the future.")
    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age

# --- 1. Age in different units ---
def age_in_days(dob: str) -> int:
    return (date.today() - _parse_dob(dob)).days

def age_in_weeks(dob: str) -> int:
    return age_in_days(dob) // 7

def age_in_months(dob: str) -> int:
    birth = _parse_dob(dob)
    today = date.today()
    return (today.year - birth.year) * 12 + today.month - birth.month

# --- 2. Next birthday info ---
def days_until_birthday(dob: str) -> int:
    birth = _parse_dob(dob)
    today = date.today()
    next_bday = date(today.year, birth.month, birth.day)
    if next_bday < today:
        next_bday = date(today.year + 1, birth.month, birth.day)
    return (next_bday - today).days

def next_birthday_weekday(dob: str) -> str:
    birth = _parse_dob(dob)
    today = date.today()
    next_bday = date(today.year, birth.month, birth.day)
    if next_bday < today:
        next_bday = date(today.year + 1, birth.month, birth.day)
    return next_bday.strftime("%A")

# --- 3. Zodiac / Star Sign ---
def zodiac_sign(dob: str) -> str:
    birth = _parse_dob(dob)
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

# --- 4. Leap year check ---
def is_leap_year(year_or_dob: object) -> bool:
    if isinstance(year_or_dob, str):
        year = _parse_dob(year_or_dob).year
    else:
        year = int(year_or_dob)
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

# --- 5. Age validation ---
def is_valid_age(dob: str) -> bool:
    try:
        age = calculate_age(dob)
        return 0 <= age <= 150
    except Exception:
        return False

# --- 6. Birthday message ---
def is_birthday(dob: str) -> bool:
    birth = _parse_dob(dob)
    today = date.today()
    return birth.month == today.month and birth.day == today.day

# --- 7. Age comparison ---
def compare_ages(dob1: str, dob2: str) -> str:
    d1, d2 = _parse_dob(dob1), _parse_dob(dob2)
    diff = abs((d1 - d2).days)
    years = diff // 365
    if d1 < d2:
        return f"Person 1 is older by approx {years} years ({diff} days)."
    elif d1 > d2:
        return f"Person 2 is older by approx {years} years ({diff} days)."
    return "They are the same age."

# --- 8. Human-readable format ---
def human_readable(dob: str) -> str:
    birth = _parse_dob(dob)
    today = date.today()
    years = today.year - birth.year
    months = today.month - birth.month
    days = today.day - birth.day
    if days < 0:
        months -= 1
        days += 30 # Approximation
    if months < 0:
        years -= 1
        months += 12
    return f"{years} years, {months} months, {days} days"

# --- 9. Age Group Classification ---
def classify_age(dob: str) -> str:
    age = calculate_age(dob)
    if age <= 2: return "Infant"
    if age <= 12: return "Child"
    if age <= 19: return "Teen"
    if age <= 64: return "Adult"
    return "Senior"

# --- 10. Multi-Cultural Approximation (Hijri-Basic) ---
def age_hijri(dob: str) -> int:
    """Approximate Hijri age (lunar year is ~354.36 days)."""
    days = age_in_days(dob)
    return int(days / 354.36)

# Short alias and Fluent API
ac = calculate_age

class Age:
    def __init__(self, dob: str):
        self.dob = dob
        self.birth_date = _parse_dob(dob)
        self.years = calculate_age(dob)
        self.days = age_in_days(dob)
        self.weeks = age_in_weeks(dob)
        self.months = age_in_months(dob)
        self.zodiac = zodiac_sign(dob)
        self.leap_year = is_leap_year(dob)
        self.next_birthday_days = days_until_birthday(dob)
        self.next_birthday_weekday = next_birthday_weekday(dob)
        self.readable = human_readable(dob)
        self.category = classify_age(dob)
        self.is_today = is_birthday(dob)
        self.hijri_age = age_hijri(dob)

    def __str__(self): return f"{self.years} years"
    def __int__(self): return self.years
