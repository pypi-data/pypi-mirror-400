"""Tests for openjobs.scraper module."""

import pytest
from openjobs.scraper import is_valid_url, _is_private_ip


class TestIsPrivateIP:
    """Tests for _is_private_ip function (SSRF protection)."""

    def test_localhost_ipv4(self):
        """Test localhost IPv4 is private."""
        assert _is_private_ip("127.0.0.1") is True

    def test_localhost_ipv6(self):
        """Test localhost IPv6 is private."""
        assert _is_private_ip("::1") is True

    def test_private_class_a(self):
        """Test Class A private IP."""
        assert _is_private_ip("10.0.0.1") is True

    def test_private_class_b(self):
        """Test Class B private IP."""
        assert _is_private_ip("172.16.0.1") is True

    def test_private_class_c(self):
        """Test Class C private IP."""
        assert _is_private_ip("192.168.1.1") is True

    def test_public_ip(self):
        """Test public IP is not private."""
        assert _is_private_ip("8.8.8.8") is False

    def test_link_local(self):
        """Test link-local IP is private."""
        assert _is_private_ip("169.254.1.1") is True

    def test_aws_metadata(self):
        """Test AWS metadata IP is private."""
        assert _is_private_ip("169.254.169.254") is True

    def test_invalid_ip(self):
        """Test invalid IP returns False."""
        assert _is_private_ip("not-an-ip") is False


class TestIsValidUrl:
    """Tests for is_valid_url function (URL validation and SSRF protection)."""

    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        is_valid, reason = is_valid_url("https://example.com/careers")
        assert is_valid is True
        assert reason == "OK"

    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        is_valid, reason = is_valid_url("http://example.com/careers")
        assert is_valid is True

    def test_empty_url(self):
        """Test empty URL is invalid."""
        is_valid, reason = is_valid_url("")
        assert is_valid is False
        assert "Empty" in reason

    def test_invalid_scheme_ftp(self):
        """Test FTP scheme is blocked."""
        is_valid, reason = is_valid_url("ftp://example.com/file")
        assert is_valid is False
        assert "scheme" in reason.lower()

    def test_invalid_scheme_file(self):
        """Test file:// scheme is blocked."""
        is_valid, reason = is_valid_url("file:///etc/passwd")
        assert is_valid is False

    def test_localhost_blocked(self):
        """Test localhost is blocked (SSRF protection)."""
        is_valid, reason = is_valid_url("http://localhost/admin")
        assert is_valid is False
        assert "Blocked" in reason or "localhost" in reason.lower()

    def test_127_0_0_1_blocked(self):
        """Test 127.0.0.1 is blocked (SSRF protection)."""
        is_valid, reason = is_valid_url("http://127.0.0.1:8080/")
        assert is_valid is False

    def test_metadata_endpoint_blocked(self):
        """Test cloud metadata endpoint is blocked (SSRF protection)."""
        is_valid, reason = is_valid_url("http://169.254.169.254/latest/meta-data/")
        assert is_valid is False

    def test_linkedin_blocked(self):
        """Test LinkedIn is in skip patterns."""
        is_valid, reason = is_valid_url("https://linkedin.com/jobs")
        assert is_valid is False
        assert "pattern" in reason.lower() or "linkedin" in reason.lower()

    def test_indeed_blocked(self):
        """Test Indeed is in skip patterns."""
        is_valid, reason = is_valid_url("https://indeed.com/jobs")
        assert is_valid is False

    def test_workday_blocked(self):
        """Test Workday is in skip patterns."""
        is_valid, reason = is_valid_url("https://company.myworkdayjobs.com/careers")
        assert is_valid is False

    def test_valid_careers_page(self):
        """Test typical careers page URL."""
        is_valid, reason = is_valid_url("https://linear.app/careers")
        assert is_valid is True

    def test_pdf_file_blocked(self):
        """Test PDF file URL is blocked."""
        is_valid, reason = is_valid_url("https://example.com/job.pdf")
        assert is_valid is False


class TestScraperIntegration:
    """Integration tests (require running services - marked as slow)."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_scrape_careers_page_returns_list(self):
        """Test scrape_careers_page returns a list."""
        from openjobs import scrape_careers_page
        # This test requires FIRECRAWL_URL and GOOGLE_API_KEY to be set
        # Skip if not configured
        import os
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not set")
        if not os.getenv("FIRECRAWL_URL"):
            pytest.skip("FIRECRAWL_URL not set")

        result = scrape_careers_page("https://linear.app/careers")
        assert isinstance(result, list)
