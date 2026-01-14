"""Mocked tests for openjobs.scraper module - no live API required."""

import pytest
from unittest.mock import patch, MagicMock
import json

from openjobs.scraper import (
    scrape_careers_page,
    scrape_with_firecrawl,
    extract_jobs_from_markdown,
    RateLimiter,
)


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_rate_limiter_creation(self):
        """Test rate limiter can be created."""
        limiter = RateLimiter(requests_per_minute=10)
        assert limiter.requests_per_minute == 10
        assert limiter.requests == []

    def test_rate_limiter_wait_under_limit(self):
        """Test wait() doesn't block when under limit."""
        limiter = RateLimiter(requests_per_minute=100)
        # Should not block
        limiter.wait()
        assert len(limiter.requests) == 1


class TestScrapeWithFirecrawlMocked:
    """Mocked tests for scrape_with_firecrawl."""

    @patch('openjobs.scraper.post_json_with_retry')
    @patch('openjobs.scraper.firecrawl_rate_limiter')
    def test_successful_scrape(self, mock_limiter, mock_post):
        """Test successful Firecrawl scrape with enough job content."""
        # Content needs:
        # - 5+ job keyword matches to pass content check
        # - 2000+ characters to pass length check
        mock_content = '''# Careers at Example Company

        Join our amazing team! We have many opportunities across engineering, design, and more.
        We are always looking for talented individuals to help us build the future.

        ## Open Positions

        ### Engineering

        - **Software Engineer** - Build amazing products with our engineering team.
          Location: San Francisco, CA | Remote OK
          We're looking for a senior engineer to join our team and work on exciting projects.

        - **Senior Developer** - Lead technical initiatives and mentor junior developers.
          Location: New York, NY
          Work on challenging problems with talented engineers and architects.

        - **Product Manager** - Define product strategy and roadmap.
          Location: Remote
          Lead product development from concept to launch with cross-functional teams.

        - **Engineering Manager** - Lead and grow our engineering organization.
          Location: San Francisco, CA
          Build high-performing teams and drive technical excellence.

        ### Design

        - **Designer** - Create beautiful user experiences that delight customers.
          Location: San Francisco, CA
          Work closely with product and engineering to bring ideas to life.

        - **Junior Designer** - Entry level design position with growth opportunities.
          Location: Remote
          Learn and grow with our design team on real projects.

        - **Senior Designer** - Lead design initiatives across multiple products.
          Location: New York, NY
          Shape the visual direction of our brand and products.

        ### Sales

        - **Account Executive** - Drive revenue growth and build relationships.
          Location: Chicago, IL
          Manage enterprise accounts and exceed quarterly targets.

        - **Sales Manager** - Lead our sales team to success.
          Location: Austin, TX
          Build and scale our sales organization with proven methodologies.

        ### Data

        - **Data Analyst** - Derive actionable insights from complex data.
          Location: Remote
          Work with our data team on analytics and business intelligence.

        - **Data Scientist** - Build ML models that power our products.
          Location: Seattle, WA
          Apply machine learning and AI to solve real-world problems.

        ## Why Work Here?

        Great benefits, amazing culture, and the opportunity to make an impact.
        We offer competitive compensation, equity, and a flexible work environment.
        Join a team of passionate individuals who love what they do.
        '''
        mock_post.return_value = {
            'data': {
                'markdown': mock_content
            }
        }

        result = scrape_with_firecrawl('https://example.com/careers')

        assert 'Software Engineer' in result
        mock_post.assert_called_once()

    @patch('openjobs.scraper.post_json_with_retry')
    @patch('openjobs.scraper.firecrawl_rate_limiter')
    def test_empty_response(self, mock_limiter, mock_post):
        """Test handling of empty Firecrawl response."""
        mock_post.return_value = {}

        result = scrape_with_firecrawl('https://example.com/careers')

        assert result == ''

    @patch('openjobs.scraper.post_json_with_retry')
    @patch('openjobs.scraper.firecrawl_rate_limiter')
    def test_exception_handling(self, mock_limiter, mock_post):
        """Test exception handling in scrape."""
        mock_post.side_effect = Exception("Network error")

        result = scrape_with_firecrawl('https://example.com/careers')

        assert result == ''


class TestExtractJobsFromMarkdownMocked:
    """Mocked tests for extract_jobs_from_markdown."""

    @patch('openjobs.scraper.requests.post')
    def test_successful_extraction(self, mock_post):
        """Test successful job extraction from markdown."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': '[{"title": "Engineer", "location": "Remote"}]'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response

        # Markdown must be > 50 chars
        long_markdown = '# Jobs at Company\n- Software Engineer - Remote\n- Product Manager - NYC\n' * 2
        result = extract_jobs_from_markdown(
            long_markdown,
            api_key='test-key'
        )

        assert len(result) == 1
        assert result[0]['title'] == 'Engineer'

    @patch('openjobs.scraper.requests.post')
    def test_extraction_with_markdown_code_block(self, mock_post):
        """Test extraction handles markdown code blocks in response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': '```json\n[{"title": "Designer"}]\n```'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response

        # Markdown must be > 50 chars
        long_markdown = '# Jobs at Company\n- Designer - Remote\n- Another role here\n' * 2
        result = extract_jobs_from_markdown(long_markdown, api_key='test-key')

        assert len(result) == 1
        assert result[0]['title'] == 'Designer'

    @patch('openjobs.scraper.requests.post')
    def test_extraction_api_error(self, mock_post):
        """Test handling of API error response."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_post.return_value = mock_response

        result = extract_jobs_from_markdown('# Jobs', api_key='test-key')

        assert result == []

    def test_extraction_no_api_key(self):
        """Test extraction fails gracefully without API key."""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': ''}):
            result = extract_jobs_from_markdown('# Jobs')
            assert result == []

    def test_extraction_empty_markdown(self):
        """Test extraction with empty markdown."""
        result = extract_jobs_from_markdown('')
        assert result == []

    def test_extraction_short_markdown(self):
        """Test extraction with too-short markdown."""
        result = extract_jobs_from_markdown('Hi')
        assert result == []

    @patch('openjobs.scraper.requests.post')
    def test_extraction_invalid_json(self, mock_post):
        """Test handling of invalid JSON in response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': 'This is not valid JSON'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response

        result = extract_jobs_from_markdown('# Jobs', api_key='test-key')

        assert result == []

    @patch('openjobs.scraper.requests.post')
    def test_extraction_filters_invalid_jobs(self, mock_post):
        """Test that jobs without titles are filtered out."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': '[{"title": "Valid"}, {"location": "NoTitle"}, {"title": ""}]'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response

        # Markdown must be > 50 chars
        long_markdown = '# Jobs at Company\n- Valid Job - Remote\n- Another role\n' * 2
        result = extract_jobs_from_markdown(long_markdown, api_key='test-key')

        assert len(result) == 1
        assert result[0]['title'] == 'Valid'


class TestScrapeCareersPageMocked:
    """Mocked tests for scrape_careers_page."""

    @patch('openjobs.scraper.extract_jobs_from_markdown')
    @patch('openjobs.scraper.scrape_with_firecrawl')
    def test_full_scrape_pipeline(self, mock_firecrawl, mock_extract):
        """Test full scraping pipeline."""
        mock_firecrawl.return_value = '# Careers\n- Engineer'
        mock_extract.return_value = [
            {'title': 'Software Engineer', 'location': 'Remote', 'url': 'https://example.com/job1'}
        ]

        result = scrape_careers_page('https://example.com/careers')

        assert len(result) == 1
        assert result[0]['title'] == 'Software Engineer'
        assert result[0]['company'] == 'example'
        assert 'slug' in result[0]
        assert 'date_scraped' in result[0]

    @patch('openjobs.scraper.extract_jobs_from_markdown')
    @patch('openjobs.scraper.scrape_with_firecrawl')
    def test_scrape_with_company_name(self, mock_firecrawl, mock_extract):
        """Test scraping with explicit company name."""
        mock_firecrawl.return_value = '# Careers'
        mock_extract.return_value = [{'title': 'Engineer'}]

        result = scrape_careers_page('https://example.com/careers', company_name='Acme Corp')

        assert result[0]['company'] == 'Acme Corp'

    @patch('openjobs.scraper.scrape_with_firecrawl')
    def test_scrape_empty_firecrawl_response(self, mock_firecrawl):
        """Test handling when Firecrawl returns empty."""
        mock_firecrawl.return_value = ''

        result = scrape_careers_page('https://example.com/careers')

        assert result == []

    @patch('openjobs.scraper.extract_jobs_from_markdown')
    @patch('openjobs.scraper.scrape_with_firecrawl')
    def test_scrape_no_jobs_found(self, mock_firecrawl, mock_extract):
        """Test handling when no jobs are extracted."""
        mock_firecrawl.return_value = '# About Us'
        mock_extract.return_value = []

        result = scrape_careers_page('https://example.com/careers')

        assert result == []

    def test_scrape_empty_url(self):
        """Test scraping with empty URL."""
        result = scrape_careers_page('')
        assert result == []

    def test_scrape_invalid_url(self):
        """Test scraping with invalid URL (SSRF blocked)."""
        result = scrape_careers_page('http://localhost/admin')
        assert result == []

    def test_scrape_adds_https(self):
        """Test that URLs without protocol get https added."""
        with patch('openjobs.scraper.scrape_with_firecrawl') as mock_fc:
            mock_fc.return_value = ''
            scrape_careers_page('example.com/careers')
            # URL should have been converted to https
            mock_fc.assert_called_once()

    @patch('openjobs.scraper.extract_jobs_from_markdown')
    @patch('openjobs.scraper.scrape_with_firecrawl')
    def test_scrape_generates_job_url_fallback(self, mock_firecrawl, mock_extract):
        """Test that jobs without URLs get fallback URL generated."""
        mock_firecrawl.return_value = '# Careers'
        mock_extract.return_value = [{'title': 'Engineer'}]  # No URL

        result = scrape_careers_page('https://example.com/careers')

        assert 'job_url' in result[0]
        assert 'example.com' in result[0]['job_url']


class TestHasJobContent:
    """Tests for _has_job_content function."""

    def test_content_with_enough_keywords(self):
        """Test content with sufficient job keywords passes."""
        from openjobs.scraper import _has_job_content
        content = "Software Engineer, Product Manager, Designer, Senior Developer, Lead Analyst"
        assert _has_job_content(content) is True

    def test_content_with_few_keywords(self):
        """Test content with too few keywords fails."""
        from openjobs.scraper import _has_job_content
        content = "We are a great company with amazing culture."
        assert _has_job_content(content) is False

    def test_empty_content(self):
        """Test empty content returns False."""
        from openjobs.scraper import _has_job_content
        assert _has_job_content("") is False
        assert _has_job_content(None) is False

    def test_case_insensitive(self):
        """Test keyword matching is case insensitive."""
        from openjobs.scraper import _has_job_content
        content = "SOFTWARE ENGINEER, PRODUCT MANAGER, DESIGNER, SENIOR DEVELOPER, ANALYST"
        assert _has_job_content(content) is True


class TestExtractEmbeddedJobs:
    """Tests for _extract_embedded_jobs function."""

    def test_extract_escaped_json_jobs(self):
        """Test extraction from escaped JSON (React/Next.js pattern)."""
        from openjobs.scraper import _extract_embedded_jobs
        html = '''<script>{"data":\\"jobs\\":[{\\"title\\":\\"Engineer\\",\\"location\\":\\"Remote\\"}],\\"other\\":\\"data\\"}</script>'''
        jobs = _extract_embedded_jobs(html)
        assert len(jobs) == 1
        assert jobs[0]['title'] == 'Engineer'

    def test_extract_json_ld_jobs(self):
        """Test extraction from JSON-LD JobPosting schema."""
        from openjobs.scraper import _extract_embedded_jobs
        html = '''
        <script type="application/ld+json">
        {"@type": "JobPosting", "title": "Software Engineer", "url": "https://example.com/job1"}
        </script>
        '''
        jobs = _extract_embedded_jobs(html)
        assert len(jobs) == 1
        assert jobs[0]['title'] == 'Software Engineer'

    def test_extract_unescaped_json_jobs(self):
        """Test extraction from unescaped JSON array."""
        from openjobs.scraper import _extract_embedded_jobs
        html = '''<script>var data = {"jobs": [{"title": "Designer"}, {"title": "Developer"}]};</script>'''
        jobs = _extract_embedded_jobs(html)
        assert len(jobs) == 2
        assert jobs[0]['title'] == 'Designer'

    def test_no_embedded_jobs(self):
        """Test returns empty list when no embedded jobs found."""
        from openjobs.scraper import _extract_embedded_jobs
        html = '<html><body><h1>Careers</h1><p>No jobs here</p></body></html>'
        jobs = _extract_embedded_jobs(html)
        assert jobs == []

    def test_malformed_json_handled(self):
        """Test malformed JSON doesn't raise exception."""
        from openjobs.scraper import _extract_embedded_jobs
        html = '''<script type="application/ld+json">{malformed json here}</script>'''
        jobs = _extract_embedded_jobs(html)
        assert jobs == []


class TestDiscoverCareersUrlMocked:
    """Mocked tests for discover_careers_url function."""

    @patch('openjobs.scraper._search_careers_with_gemini')
    @patch('openjobs.scraper._check_url_exists')
    def test_finds_common_path(self, mock_check, mock_search):
        """Test discovery finds common /careers path."""
        from openjobs.scraper import discover_careers_url
        # First call for /careers returns True
        mock_check.side_effect = [True]

        result = discover_careers_url('example.com')

        assert result == 'https://example.com/careers'
        mock_search.assert_not_called()

    @patch('openjobs.scraper._search_careers_with_gemini')
    @patch('openjobs.scraper._check_url_exists')
    def test_falls_back_to_gemini_search(self, mock_check, mock_search):
        """Test discovery falls back to Gemini search when common paths fail."""
        from openjobs.scraper import discover_careers_url
        mock_check.return_value = False
        mock_search.return_value = 'https://stripe.com/jobs/search'

        result = discover_careers_url('stripe.com', google_api_key='test-key')

        assert result == 'https://stripe.com/jobs/search'
        mock_search.assert_called_once()

    @patch('openjobs.scraper._search_careers_with_gemini')
    @patch('openjobs.scraper._check_url_exists')
    def test_returns_none_when_not_found(self, mock_check, mock_search):
        """Test returns None when careers page not found."""
        from openjobs.scraper import discover_careers_url
        mock_check.return_value = False
        mock_search.return_value = None

        result = discover_careers_url('unknown-company.com', google_api_key='test-key')

        assert result is None

    def test_cleans_domain_input(self):
        """Test domain input is cleaned properly."""
        from openjobs.scraper import discover_careers_url
        with patch('openjobs.scraper._check_url_exists') as mock_check:
            mock_check.return_value = True
            # Test with full URL input
            result = discover_careers_url('https://www.example.com/page')
            assert 'example.com' in result


class TestFetchRawHtmlMocked:
    """Mocked tests for _fetch_raw_html function."""

    @patch('openjobs.scraper.requests.get')
    def test_successful_fetch(self, mock_get):
        """Test successful raw HTML fetch."""
        from openjobs.scraper import _fetch_raw_html
        mock_response = MagicMock()
        mock_response.text = '<html><body>Content</body></html>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = _fetch_raw_html('https://example.com')

        assert '<body>Content</body>' in result
        mock_get.assert_called_once()

    @patch('openjobs.scraper.requests.get')
    def test_fetch_failure(self, mock_get):
        """Test failed fetch returns empty string."""
        from openjobs.scraper import _fetch_raw_html
        mock_get.side_effect = Exception("Network error")

        result = _fetch_raw_html('https://example.com')

        assert result == ''


class TestHtmlFallbackPath:
    """Tests for HTML fallback path in extract_jobs_from_markdown."""

    @patch('openjobs.scraper._extract_embedded_jobs')
    def test_html_marker_triggers_embedded_extraction(self, mock_extract):
        """Test RAW_HTML marker triggers embedded job extraction."""
        from openjobs.scraper import extract_jobs_from_markdown
        mock_extract.return_value = [{'title': 'Test Job'}]

        html_content = '<!-- RAW_HTML -->\n<html><body>Jobs here</body></html>'
        result = extract_jobs_from_markdown(html_content, api_key='test-key')

        assert len(result) == 1
        assert result[0]['title'] == 'Test Job'
        mock_extract.assert_called_once()

    @patch('openjobs.scraper.requests.post')
    @patch('openjobs.scraper._extract_embedded_jobs')
    def test_html_falls_back_to_gemini_when_no_embedded_jobs(self, mock_extract, mock_post):
        """Test HTML falls back to Gemini when embedded extraction fails."""
        from openjobs.scraper import extract_jobs_from_markdown
        mock_extract.return_value = []

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': '[{"title": "Gemini Job"}]'}]}}]
        }
        mock_post.return_value = mock_response

        html_content = '<!-- RAW_HTML -->\n' + '<html>' * 100  # Make content long enough
        result = extract_jobs_from_markdown(html_content, api_key='test-key')

        assert len(result) == 1
        assert result[0]['title'] == 'Gemini Job'
