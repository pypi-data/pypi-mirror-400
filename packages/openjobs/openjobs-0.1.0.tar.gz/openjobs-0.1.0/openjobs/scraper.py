"""
OpenJobs Scraper - Scrape job listings from any careers page

Uses Firecrawl for JavaScript rendering and Gemini AI for job extraction.
"""

import ipaddress
import json
import os
import re
import socket
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests

from .http_utils import post_json_with_retry
from .logger import logger
from .utils import create_slug

# Configuration
# Firecrawl Cloud: Get free API key at https://firecrawl.dev (500 credits/month free)
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
FIRECRAWL_URL = os.getenv("FIRECRAWL_URL", "https://api.firecrawl.dev")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# Firecrawl wait time configuration
DEFAULT_WAIT_MS = 5000  # Default wait for JS rendering
SLOW_SPA_WAIT_MS = 8000  # Extra time for heavy JS sites

# Patterns that need extra wait time (heavy JS career sites)
SLOW_SITE_PATTERNS = [
    'workday', 'lever.co', 'greenhouse.io', 'bamboohr',
    'careers.', 'jobs.', 'apply.', 'hire.'
]

# Heavy SPA sites that need extended wait + scroll actions
HEAVY_SPA_WAIT_MS = 15000  # 15 seconds for very heavy JS sites
HEAVY_SPA_PATTERNS = ['retool', 'airtable', 'vercel', 'notion', 'figma']

# Job-related keywords for content validation
# Used to detect if scraped content contains actual job listings
JOB_KEYWORDS = [
    'engineer', 'manager', 'designer', 'analyst', 'developer', 'director',
    'coordinator', 'specialist', 'lead', 'senior', 'junior', 'associate',
    'account executive', 'product manager', 'software engineer'
]

# Minimum keyword matches required to consider content as having job listings
MIN_JOB_KEYWORD_MATCHES = 5


def _has_job_content(content: str) -> bool:
    """
    Check if content has enough job-related keywords to indicate actual listings.

    Single mentions of job keywords could just be in descriptions or benefits text,
    so we require multiple matches to confirm the page has actual job listings.

    Args:
        content: Text content to check

    Returns:
        True if content has enough job keywords to indicate job listings
    """
    if not content:
        return False
    content_lower = content.lower()
    match_count = sum(content_lower.count(kw) for kw in JOB_KEYWORDS)
    return match_count >= MIN_JOB_KEYWORD_MATCHES


# Common careers page paths to try during discovery
COMMON_CAREERS_PATHS = [
    '/careers',
    '/jobs',
    '/careers/jobs',
    '/about/careers',
    '/company/careers',
    '/join',
    '/join-us',
    '/work-with-us',
]


class RateLimiter:
    """Rate limiter to prevent overwhelming APIs."""

    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.requests = []
        self.lock = threading.Lock()

    def wait(self):
        """Wait if necessary to stay within rate limit."""
        with self.lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)

            # Remove old requests outside the window
            self.requests = [t for t in self.requests if t > minute_ago]

            # If at limit, wait for oldest request to expire
            if len(self.requests) >= self.requests_per_minute:
                oldest = min(self.requests)
                sleep_time = (oldest + timedelta(minutes=1) - now).total_seconds()
                if sleep_time > 0:
                    logger.debug(f"Rate limit reached, waiting {sleep_time:.1f}s")
                    time.sleep(sleep_time)

            # Record this request
            self.requests.append(datetime.now())


# Global rate limiter instance
firecrawl_rate_limiter = RateLimiter(requests_per_minute=30)

# URLs that cannot be scraped or are not career pages
SKIP_URL_PATTERNS = [
    # File extensions (not pages)
    '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf', '.zip',
    # Social media / login pages (can't scrape)
    'linkedin.com', 'twitter.com', 'facebook.com', 'instagram.com',
    # Generic job boards (not company-specific)
    'indeed.com', 'glassdoor.com', 'monster.com', 'ziprecruiter.com',
    # Workday (has its own ATS - too complex to scrape)
    '.myworkdayjobs.com',
]


def _is_private_ip(ip_str: str) -> bool:
    """Check if an IP address is private, loopback, or otherwise internal."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private or
            ip.is_loopback or
            ip.is_reserved or
            ip.is_link_local or
            ip.is_multicast or
            ip.is_unspecified
        )
    except ValueError:
        return False


def is_valid_url(url: str) -> Tuple[bool, str]:
    """
    Check if a URL is valid for scraping.

    Security: Blocks SSRF attacks by validating:
    - URL scheme (only http/https)
    - No internal/private IP addresses
    - No localhost or loopback addresses

    Returns:
        (is_valid, reason) - True if valid, False with reason if not
    """
    if not url:
        return False, "Empty URL"

    url_lower = url.lower()

    # Parse URL for security checks
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format"

    # Security: Only allow http/https schemes
    if parsed.scheme not in ('http', 'https'):
        return False, f"Invalid URL scheme: {parsed.scheme} (only http/https allowed)"

    # Security: Block localhost and loopback variations
    hostname = parsed.hostname or ''
    hostname_lower = hostname.lower()

    blocked_hosts = [
        'localhost', '127.0.0.1', '::1', '0.0.0.0',
        'localhost.localdomain', 'local', 'internal',
        'metadata.google.internal',  # GCP metadata
        '169.254.169.254',  # AWS/GCP/Azure metadata endpoint
    ]

    if hostname_lower in blocked_hosts:
        return False, f"Blocked hostname: {hostname}"

    # Security: Check if hostname resolves to private/internal IP
    try:
        if _is_private_ip(hostname):
            return False, f"Private/internal IP not allowed: {hostname}"

        # For hostnames, resolve and check the IP
        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            # It's a hostname, resolve it
            try:
                resolved_ip = socket.gethostbyname(hostname)
                if _is_private_ip(resolved_ip):
                    return False, f"Hostname resolves to private IP: {hostname} -> {resolved_ip}"
            except socket.gaierror:
                pass  # DNS resolution failed - allow through
    except Exception:
        pass

    # Check for skip patterns
    for pattern in SKIP_URL_PATTERNS:
        if pattern in url_lower:
            return False, f"Skipped pattern: {pattern}"

    return True, "OK"


# Default extraction prompt for Gemini
EXTRACTION_PROMPT = """Extract all job listings from this careers page content.

IMPORTANT:
- ONLY extract jobs that are explicitly listed on the page
- Do NOT invent or assume job titles that aren't clearly stated
- If unsure whether something is a job listing, skip it
- If no jobs are clearly listed, return an empty array

For each job, return a JSON object with:
- title: job title exactly as written on the page (required)
- department: department or team name if stated (optional)
- location: job location if stated (optional)
- url: direct link to job posting if available (optional)

Return ONLY a valid JSON array. No explanation, no markdown.
If no jobs found, return: []

Example output:
[{"title": "Software Engineer", "department": "Engineering", "location": "Remote", "url": "https://..."}]"""


def _firecrawl_request(
    url: str,
    wait_ms: int,
    api_key: Optional[str] = None,
    with_scroll: bool = False
) -> str:
    """
    Make a single Firecrawl request with optional scroll actions.

    Args:
        url: The URL to scrape
        wait_ms: Milliseconds to wait for JS rendering
        api_key: Optional Firecrawl API key
        with_scroll: If True, add scroll actions (cloud Firecrawl only)

    Returns:
        Markdown content or empty string on failure
    """
    try:
        headers = {}
        firecrawl_api_key = api_key or FIRECRAWL_API_KEY
        if firecrawl_api_key:
            headers["Authorization"] = f"Bearer {firecrawl_api_key}"

        payload = {
            "url": url,
            "formats": ["markdown"],
            "waitFor": wait_ms,
            "timeout": 60000,
        }

        # Add scroll actions only for cloud Firecrawl (self-hosted doesn't support it)
        is_cloud = firecrawl_api_key or 'api.firecrawl.dev' in FIRECRAWL_URL
        if with_scroll and is_cloud:
            payload["actions"] = [
                {"type": "scroll", "direction": "down"},
                {"type": "wait", "milliseconds": 2000},
                {"type": "scroll", "direction": "down"},
                {"type": "wait", "milliseconds": 2000},
                {"type": "scroll", "direction": "down"},
            ]
            logger.debug(f"Using scroll actions for {url}")

        data = post_json_with_retry(
            f"{FIRECRAWL_URL}/v1/scrape",
            json_body=payload,
            headers=headers if headers else None,
            timeout=90 if with_scroll else 60
        )

        if not data:
            return ""

        return data.get('data', {}).get('markdown', '')

    except Exception as e:
        logger.debug(f"Firecrawl request failed: {e}")
        return ""


def _fetch_raw_html(url: str) -> str:
    """Fetch raw HTML directly as fallback when Firecrawl fails."""
    try:
        response = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.debug(f"Raw HTML fetch failed: {e}")
        return ""


def _extract_embedded_jobs(html: str) -> List[Dict]:
    """
    Extract job listings from embedded JSON in HTML.

    Many sites embed job data as JSON in React/Next.js data structures,
    JSON-LD, or script tags. This extracts jobs without needing Gemini.

    Args:
        html: Raw HTML content

    Returns:
        List of job dicts, or empty list if no embedded jobs found
    """
    jobs = []

    try:
        # Pattern 1: Escaped JSON jobs array (React/Next.js)
        # Matches: \"jobs\":[{...},{...}]
        escaped_match = re.search(r'\\"jobs\\":\[(.*?)\](?=,\\"|\}\])', html, re.DOTALL)
        if escaped_match:
            jobs_str = escaped_match.group(0).replace('\\"', '"')
            jobs_str = '{' + jobs_str + '}'
            data = json.loads(jobs_str)
            for job in data.get('jobs', []):
                if job.get('title'):
                    jobs.append({
                        'title': job.get('title'),
                        'department': job.get('department'),
                        'location': job.get('location'),
                        'url': job.get('link') or job.get('url')
                    })
            if jobs:
                logger.debug(f"Extracted {len(jobs)} jobs from escaped JSON")
                return jobs

        # Pattern 2: JSON-LD JobPosting schema
        # Matches: <script type="application/ld+json">{"@type":"JobPosting"...}</script>
        ld_matches = re.findall(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html, re.DOTALL | re.IGNORECASE
        )
        for ld_json in ld_matches:
            try:
                data = json.loads(ld_json)
                # Handle single job or array
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get('@type') == 'JobPosting':
                        jobs.append({
                            'title': item.get('title'),
                            'department': item.get('hiringOrganization', {}).get('department'),
                            'location': item.get('jobLocation', {}).get('address', {}).get('addressLocality'),
                            'url': item.get('url')
                        })
            except json.JSONDecodeError:
                continue

        if jobs:
            logger.debug(f"Extracted {len(jobs)} jobs from JSON-LD")
            return jobs

        # Pattern 3: Unescaped JSON jobs array in script tags
        # Matches: "jobs":[{...},{...}] or 'jobs':[{...},{...}]
        unescaped_match = re.search(r'"jobs"\s*:\s*\[(.*?)\]', html, re.DOTALL)
        if unescaped_match:
            try:
                jobs_str = '[' + unescaped_match.group(1) + ']'
                job_list = json.loads(jobs_str)
                for job in job_list:
                    if isinstance(job, dict) and job.get('title'):
                        jobs.append({
                            'title': job.get('title'),
                            'department': job.get('department'),
                            'location': job.get('location'),
                            'url': job.get('link') or job.get('url')
                        })
                if jobs:
                    logger.debug(f"Extracted {len(jobs)} jobs from unescaped JSON")
                    return jobs
            except json.JSONDecodeError:
                pass

    except Exception as e:
        logger.debug(f"Embedded job extraction error: {e}")

    return jobs


def scrape_with_firecrawl(url: str, api_key: Optional[str] = None) -> str:
    """
    Scrape a URL using Firecrawl and return markdown content.

    Uses tiered approach:
    1. Standard scrape with appropriate wait time
    2. For heavy SPAs, retry with extended wait + scroll actions
    3. Fallback to raw HTML if Firecrawl returns minimal content

    Args:
        url: The URL to scrape
        api_key: Optional Firecrawl API key (uses FIRECRAWL_API_KEY env var if not provided)

    Returns:
        Markdown content of the page, or empty string on failure
    """
    # Apply rate limiting before making request
    firecrawl_rate_limiter.wait()

    url_lower = url.lower()

    # Determine initial wait time based on URL patterns
    wait_time = DEFAULT_WAIT_MS
    if any(pattern in url_lower for pattern in SLOW_SITE_PATTERNS):
        wait_time = SLOW_SPA_WAIT_MS
        logger.debug(f"Using extended wait time ({wait_time}ms) for slow site: {url}")

    # Check if this is a heavy SPA site
    is_heavy_spa = any(pattern in url_lower for pattern in HEAVY_SPA_PATTERNS)

    # Attempt 1: Standard scrape
    markdown = _firecrawl_request(url, wait_time, api_key)

    # Check if we got meaningful content with job keywords
    if markdown and len(markdown) > 2000 and _has_job_content(markdown):
        return markdown

    # Attempt 2: For heavy SPAs or content without jobs, retry with extended wait
    if is_heavy_spa or not markdown or len(markdown) < 2000 or not _has_job_content(markdown):
        logger.info(f"Retrying {url} with extended wait ({HEAVY_SPA_WAIT_MS}ms)")
        firecrawl_rate_limiter.wait()
        markdown_retry = _firecrawl_request(url, HEAVY_SPA_WAIT_MS, api_key, with_scroll=True)

        # Use retry result if it's better
        if markdown_retry and len(markdown_retry) > len(markdown or ""):
            markdown = markdown_retry

        if markdown and len(markdown) > 2000 and _has_job_content(markdown):
            return markdown

    # Attempt 3: Fallback to raw HTML if Firecrawl content lacks job keywords
    # Raw HTML can contain embedded JSON that we can parse directly
    if not markdown or len(markdown) < 2000 or not _has_job_content(markdown):
        logger.info(f"Firecrawl returned minimal content, trying raw HTML fallback for {url}")
        raw_html = _fetch_raw_html(url)
        if raw_html and len(raw_html) > 5000:
            # Return HTML wrapped in a marker so extract_jobs knows it's HTML
            return f"<!-- RAW_HTML -->\n{raw_html}"

    # Return whatever we got (might be empty)
    if not markdown:
        logger.error(f"Firecrawl returned empty response for {url}")

    return markdown or ""


HTML_EXTRACTION_PROMPT = """Extract all job listings from this careers page HTML.

IMPORTANT:
- ONLY extract jobs that are explicitly listed in the HTML
- Look for job titles in elements, links, headings, or JSON data embedded in the page
- Do NOT invent or assume job titles that aren't clearly stated
- If no jobs are clearly listed, return an empty array

For each job, return a JSON object with:
- title: job title exactly as written (required)
- department: department or team name if stated (optional)
- location: job location if stated (optional)
- url: direct link to job posting if available (optional)

Return ONLY a valid JSON array. No explanation, no markdown.
If no jobs found, return: []"""


def extract_jobs_from_markdown(
    markdown: str,
    prompt: Optional[str] = None,
    api_key: Optional[str] = None
) -> List[Dict]:
    """
    Use Gemini to extract job listings from markdown or HTML content.

    Args:
        markdown: Page content as markdown (or HTML if marked with <!-- RAW_HTML -->)
        prompt: Custom extraction prompt (uses default if not provided)
        api_key: Google API key (uses GOOGLE_API_KEY env var if not provided)

    Returns:
        List of job dicts with title, department, location, url
    """
    if not markdown or len(markdown) < 50:
        return []

    google_api_key = api_key or GOOGLE_API_KEY
    if not google_api_key:
        logger.error("GOOGLE_API_KEY not set")
        return []

    # Check if content is raw HTML (fallback mode)
    is_html = markdown.startswith("<!-- RAW_HTML -->")
    if is_html:
        html_content = markdown[len("<!-- RAW_HTML -->\n"):]

        # First try: Extract embedded JSON jobs directly (fast, no API call)
        embedded_jobs = _extract_embedded_jobs(html_content)
        if embedded_jobs:
            logger.info(f"Extracted {len(embedded_jobs)} jobs from embedded JSON")
            return embedded_jobs

        # Fallback: Use Gemini to parse HTML
        markdown = html_content
        extraction_prompt = HTML_EXTRACTION_PROMPT
        content_limit = 50000
        logger.debug("Using HTML extraction mode with Gemini")
    else:
        extraction_prompt = prompt or EXTRACTION_PROMPT
        content_limit = 25000

    start_time = time.time()

    try:
        payload = {
            "contents": [{"parts": [{"text": f"{extraction_prompt}\n\nPage content:\n{markdown[:content_limit]}"}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 8192
            }
        }

        response = requests.post(
            f"{GEMINI_URL}?key={google_api_key}",
            json=payload,
            timeout=30
        )
        duration_ms = int((time.time() - start_time) * 1000)

        if response.status_code != 200:
            logger.error(f"Gemini error {response.status_code}: {response.text[:200]}")
            return []

        result = response.json()

        # Extract text from response
        text = ""
        if 'candidates' in result and result['candidates']:
            parts = result['candidates'][0].get('content', {}).get('parts', [])
            for part in parts:
                if 'text' in part:
                    text += part['text']

        if not text:
            return []

        # Parse JSON from response
        text = text.strip()
        if text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])

        start = text.find('[')
        end = text.rfind(']') + 1

        if start == -1 or end == 0:
            return []

        jobs = json.loads(text[start:end])
        logger.debug(f"Extracted {len(jobs)} jobs in {duration_ms}ms")
        return [j for j in jobs if isinstance(j, dict) and j.get('title')]

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response: {e}")
        return []
    except Exception as e:
        logger.error(f"Gemini extraction failed: {e}")
        return []


def scrape_careers_page(
    url: str,
    company_name: Optional[str] = None,
    firecrawl_api_key: Optional[str] = None,
    google_api_key: Optional[str] = None,
    extraction_prompt: Optional[str] = None
) -> List[Dict]:
    """
    Scrape job postings from a careers page using Firecrawl + Gemini.

    This is the main entry point for scraping jobs from any careers page.

    Args:
        url: The careers page URL to scrape
        company_name: Optional company name (extracted from URL if not provided)
        firecrawl_api_key: Optional Firecrawl API key
        google_api_key: Optional Google API key for Gemini
        extraction_prompt: Optional custom prompt for job extraction

    Returns:
        List of job entries with: company, job_url, slug, title, department, location, date_scraped
    """
    if not url:
        return []

    # Ensure URL has protocol
    if not url.startswith('http'):
        url = f'https://{url}'

    # Validate URL before scraping
    is_valid, reason = is_valid_url(url)
    if not is_valid:
        logger.info(f"Skipping invalid URL: {url} ({reason})")
        return []

    # Extract company name from URL if not provided
    if not company_name:
        try:
            parsed = urlparse(url)
            company_name = parsed.netloc.replace('www.', '').split('.')[0]
        except Exception:
            company_name = "unknown"

    logger.info(f"Scraping {company_name} careers page: {url}")

    # Step 1: Scrape page with Firecrawl
    markdown = scrape_with_firecrawl(url, api_key=firecrawl_api_key)
    if not markdown:
        logger.warning(f"No content from Firecrawl for {url}")
        return []

    # Step 2: Extract jobs with Gemini
    jobs = extract_jobs_from_markdown(
        markdown,
        prompt=extraction_prompt,
        api_key=google_api_key
    )
    if not jobs:
        logger.info(f"No jobs extracted from {url}")
        return []

    logger.info(f"Extracted {len(jobs)} jobs from {company_name}")

    # Step 3: Format output
    jobs_data = []
    now = datetime.now().isoformat()

    for idx, job in enumerate(jobs):
        title = job.get('title', '')
        job_url = job.get('url') or f"{url}#job-{idx}"

        job_entry = {
            "company": company_name,
            "title": title,
            "department": job.get('department'),
            "location": job.get('location'),
            "job_url": job_url,
            "slug": create_slug(company_name, title),
            "date_scraped": now,
            "source_url": url
        }

        jobs_data.append(job_entry)

    return jobs_data


def _check_url_exists(url: str) -> bool:
    """Quick HEAD request to check if URL exists and returns 200."""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except Exception:
        return False


def _search_careers_with_gemini(domain: str, api_key: str) -> Optional[str]:
    """
    Use Gemini with Google Search grounding to find careers page.

    Args:
        domain: Company domain (e.g., "stripe.com")
        api_key: Google API key

    Returns:
        Best careers page URL or None
    """
    try:
        prompt = f"""Find the careers or jobs page URL for {domain}.

I need the exact URL where job listings are displayed, not just a landing page.
For example, stripe.com's jobs are at stripe.com/jobs/search, not stripe.com/jobs.

Return ONLY the URL, nothing else. If you cannot find it, return "NONE"."""

        response = requests.post(
            f"{GEMINI_URL}?key={api_key}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "tools": [{"google_search": {}}],
                "generationConfig": {"temperature": 0.1}
            },
            timeout=30
        )

        if response.status_code != 200:
            logger.debug(f"Gemini search failed: {response.status_code}")
            return None

        result = response.json()

        # Extract text from response
        text = ""
        if 'candidates' in result and result['candidates']:
            parts = result['candidates'][0].get('content', {}).get('parts', [])
            for part in parts:
                if 'text' in part:
                    text += part['text']

        text = text.strip()
        if not text or text.upper() == "NONE":
            return None

        # Extract URL from response (might have extra text or markdown)
        # Try full URL first (stop at common terminators)
        url_match = re.search(r'https?://[^\s<>"\')\]]+', text)
        if url_match:
            found_url = url_match.group(0).rstrip('.,;:')
            if domain.replace('www.', '') in found_url:
                return found_url

        # Try domain/path pattern (e.g., "stripe.com/jobs")
        domain_path_match = re.search(rf'{re.escape(domain)}[/\w-]*', text, re.IGNORECASE)
        if domain_path_match:
            found_path = domain_path_match.group(0).rstrip('.,;:')
            return f"https://{found_path}"

        return None

    except Exception as e:
        logger.debug(f"Gemini search error: {e}")
        return None


def discover_careers_url(
    domain: str,
    google_api_key: Optional[str] = None
) -> Optional[str]:
    """
    Discover the careers page URL for a company domain.

    Uses a two-step approach:
    1. Try common paths (/careers, /jobs, etc.) - no API cost
    2. If not found, use Gemini with Google Search grounding

    Args:
        domain: Company domain (e.g., "stripe.com", "anthropic.com")
        google_api_key: Optional Google API key (uses env var if not provided)

    Returns:
        Best careers page URL or None if not found

    Example:
        >>> discover_careers_url("stripe.com")
        'https://stripe.com/jobs/search'
    """
    # Clean domain
    domain = domain.lower().strip()
    if domain.startswith('http'):
        domain = urlparse(domain).netloc
    domain = domain.replace('www.', '')

    logger.info(f"Discovering careers page for {domain}")

    # Step 1: Try common paths (free, no API call)
    base_url = f"https://{domain}"
    for path in COMMON_CAREERS_PATHS:
        test_url = f"{base_url}{path}"
        if _check_url_exists(test_url):
            logger.info(f"Found careers page at common path: {test_url}")
            return test_url

    # Also try with www
    base_url_www = f"https://www.{domain}"
    for path in COMMON_CAREERS_PATHS:
        test_url = f"{base_url_www}{path}"
        if _check_url_exists(test_url):
            logger.info(f"Found careers page at common path: {test_url}")
            return test_url

    # Step 2: Use Gemini with Google Search
    api_key = google_api_key or GOOGLE_API_KEY
    if not api_key:
        logger.warning("No Google API key for Gemini search")
        return None

    logger.info(f"Searching for {domain} careers page with Gemini...")
    found_url = _search_careers_with_gemini(domain, api_key)

    if found_url:
        logger.info(f"Found careers page via search: {found_url}")
        return found_url

    logger.info(f"Could not find careers page for {domain}")
    return None


def main():
    """CLI entry point for openjobs scraper."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: openjobs <careers_url> [company_name]")
        print("\nExample:")
        print("  openjobs https://linear.app/careers Linear")
        sys.exit(1)

    url = sys.argv[1]
    company = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"\nScraping: {url}")
    print("-" * 50)

    jobs = scrape_careers_page(url, company)

    if jobs:
        print(f"\nFound {len(jobs)} jobs:\n")
        for job in jobs:
            print(f"  - {job['title']}")
            if job.get('department'):
                print(f"    Department: {job['department']}")
            if job.get('location'):
                print(f"    Location: {job['location']}")
            print()
    else:
        print("\nNo jobs found.")


# CLI interface
if __name__ == "__main__":
    main()
