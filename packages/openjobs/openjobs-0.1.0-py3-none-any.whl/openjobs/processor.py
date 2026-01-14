"""
OpenJobs Processor - AI-powered job enrichment using Gemini

Enhance scraped job listings with structured data extraction.
"""

import json
import os
import re
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from .logger import logger

# Gemini API configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
MODEL_NAME = os.getenv("GEMINI_PROCESSOR_MODEL", "gemini-2.0-flash")
MAX_TOKENS = 8192
TEMPERATURE = 0.2


def _load_config() -> Dict:
    """Load configuration from config/tech_stacks.json"""
    config_path = Path(__file__).parent / 'config' / 'tech_stacks.json'
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to load config: {e}. Using defaults.")
        return {
            "allowed_tech_stacks": ["Python", "JavaScript", "Docker", "AWS"],
            "allowed_contract_types": ["Full-Time", "Part-Time", "Contract", "Freelance", "Internship", "Other"],
            "allowed_categories": ["Software Engineering", "Data", "Other Engineering", "Product", "Design",
                                   "Operations & Strategy", "Sales & Account Management", "Marketing",
                                   "People/HR/Recruitment", "Finance/Legal & Compliance", "No Match Found"]
        }


_config = _load_config()
ALLOWED_TECH_STACKS = _config.get("allowed_tech_stacks", [])
ALLOWED_CONTRACT_TYPES = _config.get("allowed_contract_types", [])
ALLOWED_CATEGORIES = _config.get("allowed_categories", [])

# Job categories with subcategories
CATEGORY_SUBCATEGORIES = {
    "Software Engineering": [
        "Backend Engineer", "DevOps & Infrastructure", "Embedded Engineer",
        "Engineering Management", "Frontend Engineer", "Full-stack Engineer",
        "Game Engineer", "Mobile Engineer", "QA & Testing Engineer",
        "Sales & Solutions Engineer", "Security Engineer", "Software Architect",
        "Support Engineer"
    ],
    "Data": [
        "Data Analysis & BI", "Data Engineer", "Data Scientist",
        "Machine Learning Engineer", "Research Engineer"
    ],
    "Other Engineering": [
        "Hardware Engineer", "IT Support", "Mechanical Engineer",
        "Technical Writer", "Other Engineering Roles"
    ],
    "Product": [
        "Delivery Manager & Agile Coach", "Product Analyst", "Product Management",
        "Technical Product Management", "User Research"
    ],
    "Design": [
        "Brand Design", "Graphic & Motion Design", "Industrial Design",
        "Product Design (UI/UX)", "UX Writer"
    ],
    "Operations & Strategy": [
        "Business Operations & Strategy", "Customer Service & Support",
        "Operations Generalist", "Project & Programme Management"
    ],
    "Sales & Account Management": [
        "Account Executive", "Customer Success & Account Management",
        "Enterprise Sales", "Partnerships", "Sales & Business Development",
        "Sales Leadership & Management", "Sales Operations", "Technical Account Management"
    ],
    "Marketing": [
        "Brand & Creative Marketing", "Content Marketing & Design", "Copywriter",
        "CRM & Marketing Operations", "Generalist Marketing", "Growth Marketing",
        "Performance Marketing", "PR & Communications", "Product Marketing",
        "SEO Marketing", "Social Media & Community"
    ],
    "People/HR/Recruitment": [
        "Administration", "Executive Assistant", "Generalist Recruitment",
        "Human Resources", "People Operations", "Technical Recruitment"
    ],
    "Finance/Legal & Compliance": [
        "Accounting & Financial Planning", "Accounts & Payroll", "Corporate Finance",
        "Finance Operations", "Legal", "Risk & Compliance"
    ],
}


class RateLimiter:
    """Rate limiter for API calls."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = []
        self.lock = threading.Lock()

    def wait(self):
        with self.lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            self.requests = [t for t in self.requests if t > minute_ago]

            if len(self.requests) >= self.requests_per_minute:
                oldest = min(self.requests)
                sleep_time = (oldest + timedelta(minutes=1) - now).total_seconds()
                if sleep_time > 0:
                    time.sleep(sleep_time)

            self.requests.append(now)


gemini_rate_limiter = RateLimiter(requests_per_minute=60)


def _sanitize_text(value: str) -> str:
    """Clean up text for API calls."""
    if not value:
        return ""
    value = re.sub(r'\s+', ' ', value)
    return value.strip()


def _call_gemini(prompt: str, api_key: Optional[str] = None) -> Optional[Dict]:
    """
    Call Gemini API and return parsed JSON response.

    Args:
        prompt: The prompt to send to Gemini
        api_key: Optional API key (uses GOOGLE_API_KEY env var if not provided)

    Returns:
        Parsed JSON response or None on failure
    """
    google_api_key = api_key or GOOGLE_API_KEY
    if not google_api_key:
        logger.error("GOOGLE_API_KEY not set")
        return None

    gemini_rate_limiter.wait()

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={google_api_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
            }
        }

        response = requests.post(url, json=payload, timeout=60)

        if response.status_code != 200:
            logger.error(f"Gemini API error {response.status_code}: {response.text[:200]}")
            return None

        result = response.json()

        if "candidates" in result and len(result["candidates"]) > 0:
            text = result["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "")

            if text:
                # Clean up markdown code blocks
                text = text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

                return json.loads(text)

        return None

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response: {e}")
        return None
    except Exception as e:
        logger.error(f"Gemini call failed: {e}")
        return None


def classify_job(job_title: str, api_key: Optional[str] = None) -> Dict[str, str]:
    """
    Classify a job title into category and subcategory.

    Args:
        job_title: The job title to classify
        api_key: Optional Google API key

    Returns:
        Dict with category, subcategory, and similar_job_title
    """
    safe_title = _sanitize_text(job_title)

    prompt = f"""Classify the job title "{safe_title}" into:

1. **category**: Select from: {ALLOWED_CATEGORIES}
2. **subcategory**: Select the most relevant subcategory
3. **similar_job_title**: A normalized version of the job title

Categories and their subcategories:
{json.dumps(CATEGORY_SUBCATEGORIES, indent=2)}

Respond with JSON only:
{{"category": "...", "subcategory": "...", "similar_job_title": "..."}}
"""

    result = _call_gemini(prompt, api_key)

    if not result:
        return {"category": "No Match Found", "subcategory": "No Match Found", "similar_job_title": job_title}

    # Validate category
    if result.get("category") not in ALLOWED_CATEGORIES:
        result["category"] = "No Match Found"
        result["subcategory"] = "No Match Found"

    return result


def enhance_job_output(
    job_title: str,
    job_description: str = "",
    company_info: str = "",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enhance job data with AI-extracted fields.

    Args:
        job_title: Job title
        job_description: Raw job description text
        company_info: Optional company context
        api_key: Optional Google API key

    Returns:
        Dict with enhanced job fields
    """
    safe_title = _sanitize_text(job_title)
    safe_desc = _sanitize_text(job_description)[:15000]  # Limit size
    safe_company = _sanitize_text(company_info)

    prompt = f"""Extract structured data from this job posting:

Job Title: {safe_title}
Description: {safe_desc}
Company Info: {safe_company}

Return a JSON object with these fields:
- simplified_job_title: Clean job title without seniority/gender/location
- tech_stack: List of technologies from allowed list: {ALLOWED_TECH_STACKS[:50]}...
- experience_required: e.g., "3-5 years" or "Not Specified"
- education_level: e.g., "Bachelor's Degree" or "Not Specified"
- salary_range: e.g., "$80,000 - $120,000 per year" or "Not Specified"
- location: Job location
- remote_type: "Remote", "Hybrid", "On-Site", or "Not Specified"
- contract_type: From {ALLOWED_CONTRACT_TYPES}
- benefits: List of benefits mentioned
- requirements: Key requirements as list

Respond with valid JSON only.
"""

    result = _call_gemini(prompt, api_key)

    if not result:
        return {
            "simplified_job_title": job_title,
            "tech_stack": [],
            "experience_required": "Not Specified",
            "education_level": "Not Specified",
            "salary_range": "Not Specified",
            "location": "Not Specified",
            "remote_type": "Not Specified",
            "contract_type": "Not Specified",
            "benefits": [],
            "requirements": []
        }

    # Filter tech stack to allowed values
    if "tech_stack" in result:
        result["tech_stack"] = [t for t in result.get("tech_stack", []) if t in ALLOWED_TECH_STACKS]

    # Validate contract type
    if result.get("contract_type") not in ALLOWED_CONTRACT_TYPES:
        result["contract_type"] = "Other"

    return result


def process_job(
    job: Dict[str, Any],
    enrich: bool = True,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a scraped job with optional AI enrichment.

    Args:
        job: Raw job dict from scraper (must have 'title' field)
        enrich: Whether to use AI enrichment (default True)
        api_key: Optional Google API key

    Returns:
        Processed job dict with all fields
    """
    title = job.get("title", "")
    if not title:
        logger.warning("Job has no title, skipping")
        return None

    # Start with base fields from scraped job
    processed = {
        "company": job.get("company", ""),
        "job_url": job.get("job_url", ""),
        "slug": job.get("slug", ""),
        "title_original": title,
        "department": job.get("department"),
        "location": job.get("location"),
        "date_scraped": job.get("date_scraped", datetime.now().isoformat()),
        "source_url": job.get("source_url", ""),
    }

    if not enrich:
        # Return basic processing without AI
        processed["title_simplified"] = title
        processed["category"] = "No Match Found"
        processed["subcategory"] = "No Match Found"
        return processed

    # AI enrichment
    logger.info(f"Enriching job: {title}")

    # Classify job
    classification = classify_job(title, api_key)
    processed["category"] = classification.get("category", "No Match Found")
    processed["subcategory"] = classification.get("subcategory", "No Match Found")
    processed["similar_title"] = classification.get("similar_job_title", title)

    # Skip non-matching categories if desired
    if processed["category"] == "No Match Found":
        logger.debug(f"Job '{title}' did not match any category")

    # Enhance with additional fields
    description = job.get("description", "")
    if description:
        enhanced = enhance_job_output(title, description, api_key=api_key)
        processed.update({
            "title_simplified": enhanced.get("simplified_job_title", title),
            "tech_stack": enhanced.get("tech_stack", []),
            "experience_required": enhanced.get("experience_required", "Not Specified"),
            "education_level": enhanced.get("education_level", "Not Specified"),
            "salary_range": enhanced.get("salary_range", "Not Specified"),
            "remote_type": enhanced.get("remote_type", "Not Specified"),
            "contract_type": enhanced.get("contract_type", "Not Specified"),
            "benefits": enhanced.get("benefits", []),
            "requirements": enhanced.get("requirements", []),
        })
    else:
        processed["title_simplified"] = classification.get("similar_job_title", title)

    return processed


def process_jobs(
    jobs: List[Dict[str, Any]],
    enrich: bool = True,
    api_key: Optional[str] = None,
    filter_categories: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Process multiple jobs with optional filtering.

    Args:
        jobs: List of raw job dicts from scraper
        enrich: Whether to use AI enrichment
        api_key: Optional Google API key
        filter_categories: If provided, only return jobs in these categories

    Returns:
        List of processed job dicts
    """
    processed_jobs = []

    for job in jobs:
        processed = process_job(job, enrich=enrich, api_key=api_key)

        if processed is None:
            continue

        # Filter by category if requested
        if filter_categories:
            if processed.get("category") not in filter_categories:
                logger.debug(f"Filtered out job '{processed.get('title_original')}' - category: {processed.get('category')}")
                continue

        processed_jobs.append(processed)

    logger.info(f"Processed {len(processed_jobs)} jobs (from {len(jobs)} total)")
    return processed_jobs
