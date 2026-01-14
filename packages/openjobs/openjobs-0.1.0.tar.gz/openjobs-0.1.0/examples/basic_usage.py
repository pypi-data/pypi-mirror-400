"""
OpenJobs - Basic Usage Example

This example shows how to scrape jobs from a careers page
and optionally enrich them with AI.

Requirements:
    # Google API key (required) - free at https://aistudio.google.com/apikey
    export GOOGLE_API_KEY=your_key

    # Option 1: Self-hosted Firecrawl (free, unlimited)
    # Run: docker compose up -d
    export FIRECRAWL_URL=http://localhost:3002

    # Option 2: Firecrawl Cloud (500 free/month)
    # export FIRECRAWL_API_KEY=your_key
"""

import json
from openjobs import scrape_careers_page, process_jobs, discover_careers_url

# Example 1: Discover careers page from domain
print("=" * 60)
print("Example 1: Discover Careers Page")
print("=" * 60)

# Find careers page URL from just the domain
careers_url = discover_careers_url("stripe.com")
print(f"\nstripe.com careers page: {careers_url}")

# Example 2: Basic scraping
print("=" * 60)
print("Example 2: Basic Scraping")
print("=" * 60)

jobs = scrape_careers_page(
    url="https://linear.app/careers",
    company_name="Linear"
)

print(f"\nFound {len(jobs)} jobs:\n")
for job in jobs[:5]:  # Show first 5
    print(f"  - {job['title']}")
    if job.get('department'):
        print(f"    Department: {job['department']}")
    if job.get('location'):
        print(f"    Location: {job['location']}")
    print(f"    URL: {job['job_url']}")
    print()

# Example 3: With AI enrichment
print("=" * 60)
print("Example 3: With AI Enrichment")
print("=" * 60)

if jobs:
    # Process jobs with AI enrichment
    enriched = process_jobs(jobs, enrich=True)

    print(f"\nEnriched {len(enriched)} jobs:\n")
    for job in enriched[:3]:  # Show first 3
        print(f"  Title: {job['title_original']}")
        print(f"  Category: {job.get('category', 'N/A')}")
        print(f"  Subcategory: {job.get('subcategory', 'N/A')}")
        if job.get('tech_stack'):
            print(f"  Tech Stack: {', '.join(job['tech_stack'][:5])}")
        if job.get('salary_range') and job.get('salary_range') != 'Not Specified':
            print(f"  Salary: {job['salary_range']}")
        print()

# Example 4: Filter by category
print("=" * 60)
print("Example 4: Filter by Category")
print("=" * 60)

if jobs:
    # Only get Software Engineering jobs
    engineering_jobs = process_jobs(
        jobs,
        enrich=True,
        filter_categories=["Software Engineering", "Data"]
    )

    print(f"\nFound {len(engineering_jobs)} engineering/data jobs")

# Example 5: Export to JSON
print("=" * 60)
print("Example 5: Export to JSON")
print("=" * 60)

if jobs:
    output_file = "scraped_jobs.json"
    with open(output_file, 'w') as f:
        json.dump(jobs, f, indent=2)
    print(f"\nExported {len(jobs)} jobs to {output_file}")

print("\nDone!")
