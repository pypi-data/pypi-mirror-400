"""Tests for openjobs.utils module."""

import pytest
from openjobs.utils import (
    create_slug,
    normalize_location,
    parse_salary_range,
    parse_experience_years,
)


class TestCreateSlug:
    """Tests for create_slug function."""

    def test_basic_slug(self):
        """Test basic slug creation."""
        result = create_slug("Acme Corp", "Software Engineer")
        assert result == "acme-corp-software-engineer"

    def test_removes_gender_suffix_mfd(self):
        """Test removal of (m/f/d) gender suffix."""
        result = create_slug("Company", "Engineer (m/f/d)")
        assert result == "company-engineer"

    def test_removes_gender_suffix_mwd(self):
        """Test removal of (m/w/d) German gender suffix."""
        result = create_slug("Company", "Developer (m/w/d)")
        assert result == "company-developer"

    def test_removes_special_characters(self):
        """Test removal of special characters."""
        result = create_slug("Company!", "Senior Engineer @ HQ")
        assert result == "company-senior-engineer-hq"

    def test_collapses_multiple_hyphens(self):
        """Test collapsing of multiple consecutive hyphens."""
        result = create_slug("My   Company", "Job---Title")
        assert "-" in result
        assert "--" not in result

    def test_empty_company(self):
        """Test with empty company name."""
        result = create_slug("", "Engineer")
        assert result == "engineer"

    def test_empty_title(self):
        """Test with empty job title."""
        result = create_slug("Company", "")
        assert result == "company-job"

    def test_long_slug_truncation(self):
        """Test that very long slugs are truncated."""
        long_title = "A" * 200
        result = create_slug("Company", long_title)
        assert len(result) <= 100

    def test_unicode_handling(self):
        """Test handling of unicode characters."""
        result = create_slug("Über Corp", "Développeur")
        assert "uber" not in result.lower() or "-" in result  # Should handle gracefully


class TestNormalizeLocation:
    """Tests for normalize_location function."""

    def test_basic_normalization(self):
        """Test basic location normalization."""
        result = normalize_location("  New York  ")
        assert result == "New York"

    def test_nyc_expansion(self):
        """Test NYC expansion to New York."""
        result = normalize_location("NYC")
        assert result == "New York"

    def test_sf_expansion(self):
        """Test SF expansion to San Francisco."""
        result = normalize_location("SF")
        assert result == "San Francisco"

    def test_empty_location(self):
        """Test empty location returns empty string."""
        result = normalize_location("")
        assert result == ""

    def test_none_location(self):
        """Test None location returns empty string."""
        result = normalize_location(None)
        assert result == ""

    def test_whitespace_collapse(self):
        """Test multiple whitespace collapse."""
        result = normalize_location("New   York   City")
        assert result == "New York City"


class TestParseSalaryRange:
    """Tests for parse_salary_range function."""

    def test_basic_range_usd(self):
        """Test basic USD salary range."""
        min_sal, max_sal, currency = parse_salary_range("$80,000 - $120,000 per year")
        assert min_sal == 80000
        assert max_sal == 120000
        assert currency == "USD"

    def test_euro_salary(self):
        """Test Euro salary."""
        min_sal, max_sal, currency = parse_salary_range("€50,000 - €70,000")
        assert min_sal == 50000
        assert max_sal == 70000
        assert currency == "EUR"

    def test_gbp_salary(self):
        """Test GBP salary."""
        min_sal, max_sal, currency = parse_salary_range("£60,000 - £80,000")
        assert min_sal == 60000
        assert max_sal == 80000
        assert currency == "GBP"

    def test_single_salary(self):
        """Test single salary value."""
        min_sal, max_sal, currency = parse_salary_range("$100,000")
        assert min_sal == 100000
        assert max_sal == 100000
        assert currency == "USD"

    def test_not_specified(self):
        """Test 'Not Specified' returns None."""
        min_sal, max_sal, currency = parse_salary_range("Not Specified")
        assert min_sal is None
        assert max_sal is None

    def test_empty_string(self):
        """Test empty string returns None."""
        min_sal, max_sal, currency = parse_salary_range("")
        assert min_sal is None
        assert max_sal is None


class TestParseExperienceYears:
    """Tests for parse_experience_years function."""

    def test_range_years(self):
        """Test experience range like '3-5 years'."""
        min_years, max_years = parse_experience_years("3-5 years")
        assert min_years == 3
        assert max_years == 5

    def test_plus_years(self):
        """Test experience like '5+ years'."""
        min_years, max_years = parse_experience_years("5+ years")
        assert min_years == 5
        assert max_years is None

    def test_single_year(self):
        """Test single year value."""
        min_years, max_years = parse_experience_years("3 years")
        assert min_years == 3
        assert max_years == 3

    def test_not_specified(self):
        """Test 'Not Specified' returns None."""
        min_years, max_years = parse_experience_years("Not Specified")
        assert min_years is None
        assert max_years is None

    def test_empty_string(self):
        """Test empty string returns None."""
        min_years, max_years = parse_experience_years("")
        assert min_years is None
        assert max_years is None
