"""
OpenJobs Utilities - Helper functions for job processing
"""

import re


def create_slug(company_name: str, job_title: str) -> str:
    """
    Create a clean, URL-friendly slug from company name and job title.

    Removes:
    - Gender suffixes like (m/f/d), (m/w/d), (f/m/d), (m/f/x), etc.
    - Special characters
    - Consecutive hyphens
    - Leading/trailing hyphens

    Args:
        company_name: Name of the company
        job_title: Title of the job

    Returns:
        Clean URL slug like "company-name-job-title"

    Example:
        >>> create_slug("Acme Corp", "Senior Software Engineer (m/f/d)")
        'acme-corp-senior-software-engineer'
    """
    # Normalize inputs
    company_name = (company_name or "").strip()
    job_title = (job_title or "job").strip()

    # Remove common gender suffixes (German/international style)
    gender_patterns = [
        r'\s*\([mfwdx]/[mfwdx]/[mfwdx]\)\s*',  # (m/f/d), (m/w/d), etc.
        r'\s*\([mfwdx]/[mfwdx]\)\s*',           # (m/f), (m/w), etc.
        r'\s*-\s*[mfwdx]/[mfwdx]/[mfwdx]\s*',   # - m/f/d
        r'\s*-\s*[mfwdx]/[mfwdx]\s*',           # - m/f
        r'\s*\(all genders?\)\s*',              # (all genders)
        r'\s*\(any gender\)\s*',                # (any gender)
        r'\s*\(diverse\)\s*',                   # (diverse)
    ]

    for pattern in gender_patterns:
        job_title = re.sub(pattern, '', job_title, flags=re.IGNORECASE)

    # Combine company and job title
    combined = f"{company_name}-{job_title}"

    # Convert to lowercase
    slug = combined.lower()

    # Replace special characters with hyphens
    slug = re.sub(r'[^a-z0-9-]', '-', slug)

    # Collapse multiple consecutive hyphens into one
    slug = re.sub(r'-+', '-', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    # Limit slug length (URLs should be reasonable)
    if len(slug) > 100:
        slug = slug[:100]
        last_hyphen = slug.rfind('-')
        if last_hyphen > 50:
            slug = slug[:last_hyphen]

    return slug or "job"


def normalize_location(location: str) -> str:
    """
    Normalize a location string.

    Args:
        location: Raw location string

    Returns:
        Normalized location
    """
    if not location:
        return ""

    # Clean up whitespace
    location = re.sub(r'\s+', ' ', location).strip()

    # Common normalizations
    location = location.replace("NYC", "New York")
    location = location.replace("SF", "San Francisco")
    location = location.replace("LA", "Los Angeles")

    return location


def parse_salary_range(salary_str: str) -> tuple:
    """
    Parse salary string into min/max/currency.

    Args:
        salary_str: Salary string like "$80,000 - $120,000 per year"

    Returns:
        Tuple of (min_salary, max_salary, currency) or (None, None, None)
    """
    if not salary_str or salary_str == "Not Specified":
        return None, None, None

    # Detect currency
    currency = None
    if '$' in salary_str or 'USD' in salary_str.upper():
        currency = 'USD'
    elif '€' in salary_str or 'EUR' in salary_str.upper():
        currency = 'EUR'
    elif '£' in salary_str or 'GBP' in salary_str.upper():
        currency = 'GBP'
    elif 'CHF' in salary_str.upper():
        currency = 'CHF'

    # Remove currency symbols and commas
    clean_str = re.sub(r'[€$£,]', '', salary_str)

    # Find all numbers
    numbers = re.findall(r'(\d+(?:\.\d+)?)', clean_str)

    if len(numbers) >= 2:
        return int(float(numbers[0])), int(float(numbers[1])), currency
    elif len(numbers) == 1:
        sal = int(float(numbers[0]))
        return sal, sal, currency

    return None, None, currency


def parse_experience_years(experience_str: str) -> tuple:
    """
    Parse experience string into min/max years.

    Args:
        experience_str: Experience string like "3-5 years" or "5+ years"

    Returns:
        Tuple of (min_years, max_years) or (None, None)
    """
    if not experience_str or experience_str == "Not Specified":
        return None, None

    exp_lower = experience_str.lower().strip()

    # Handle "10+ Years" pattern
    match = re.search(r'(\d+)\s*\+', exp_lower)
    if match:
        return int(match.group(1)), None

    # Handle "3-5 years" pattern
    match = re.search(r'(\d+)\s*[-–]\s*(\d+)', exp_lower)
    if match:
        return int(match.group(1)), int(match.group(2))

    # Handle single number
    match = re.search(r'(\d+)', exp_lower)
    if match:
        years = int(match.group(1))
        return years, years

    return None, None
