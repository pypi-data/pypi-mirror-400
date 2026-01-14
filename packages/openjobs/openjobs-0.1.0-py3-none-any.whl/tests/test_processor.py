"""Tests for openjobs.processor module."""

import pytest
from openjobs.processor import (
    _sanitize_text,
    process_job,
    process_jobs,
    ALLOWED_CATEGORIES,
    CATEGORY_SUBCATEGORIES,
)


class TestSanitizeText:
    """Tests for _sanitize_text function."""

    def test_basic_cleanup(self):
        """Test basic whitespace cleanup."""
        result = _sanitize_text("  hello   world  ")
        assert result == "hello world"

    def test_newline_removal(self):
        """Test newline removal."""
        result = _sanitize_text("hello\nworld")
        assert result == "hello world"

    def test_tab_removal(self):
        """Test tab removal."""
        result = _sanitize_text("hello\tworld")
        assert result == "hello world"

    def test_empty_string(self):
        """Test empty string returns empty."""
        result = _sanitize_text("")
        assert result == ""

    def test_none_value(self):
        """Test None returns empty string."""
        result = _sanitize_text(None)
        assert result == ""


class TestProcessJobWithoutEnrichment:
    """Tests for process_job without AI enrichment."""

    def test_basic_processing(self):
        """Test basic job processing without enrichment."""
        job = {
            "title": "Software Engineer",
            "company": "TestCo",
            "location": "Remote",
            "job_url": "https://example.com/job",
            "slug": "testco-software-engineer",
        }
        result = process_job(job, enrich=False)

        assert result is not None
        assert result["title_original"] == "Software Engineer"
        assert result["company"] == "TestCo"
        assert result["location"] == "Remote"
        assert result["category"] == "No Match Found"

    def test_missing_title_returns_none(self):
        """Test job without title returns None."""
        job = {
            "company": "TestCo",
            "location": "Remote",
        }
        result = process_job(job, enrich=False)
        assert result is None

    def test_empty_title_returns_none(self):
        """Test job with empty title returns None."""
        job = {
            "title": "",
            "company": "TestCo",
        }
        result = process_job(job, enrich=False)
        assert result is None


class TestProcessJobsWithoutEnrichment:
    """Tests for process_jobs without AI enrichment."""

    def test_process_multiple_jobs(self):
        """Test processing multiple jobs."""
        jobs = [
            {"title": "Engineer", "company": "A"},
            {"title": "Designer", "company": "B"},
            {"title": "Manager", "company": "C"},
        ]
        results = process_jobs(jobs, enrich=False)

        assert len(results) == 3
        assert results[0]["title_original"] == "Engineer"
        assert results[1]["title_original"] == "Designer"
        assert results[2]["title_original"] == "Manager"

    def test_filters_invalid_jobs(self):
        """Test that jobs without titles are filtered out."""
        jobs = [
            {"title": "Engineer", "company": "A"},
            {"company": "B"},  # No title
            {"title": "", "company": "C"},  # Empty title
            {"title": "Designer", "company": "D"},
        ]
        results = process_jobs(jobs, enrich=False)

        assert len(results) == 2
        assert results[0]["title_original"] == "Engineer"
        assert results[1]["title_original"] == "Designer"

    def test_empty_list(self):
        """Test empty job list returns empty list."""
        results = process_jobs([], enrich=False)
        assert results == []


class TestCategoryConfiguration:
    """Tests for category configuration."""

    def test_allowed_categories_not_empty(self):
        """Test ALLOWED_CATEGORIES is populated."""
        assert len(ALLOWED_CATEGORIES) > 0

    def test_software_engineering_in_categories(self):
        """Test Software Engineering is an allowed category."""
        assert "Software Engineering" in ALLOWED_CATEGORIES

    def test_no_match_found_in_categories(self):
        """Test 'No Match Found' is an allowed category."""
        assert "No Match Found" in ALLOWED_CATEGORIES

    def test_category_subcategories_mapping(self):
        """Test category subcategories mapping exists."""
        assert "Software Engineering" in CATEGORY_SUBCATEGORIES
        assert len(CATEGORY_SUBCATEGORIES["Software Engineering"]) > 0

    def test_backend_engineer_subcategory(self):
        """Test Backend Engineer is a subcategory of Software Engineering."""
        assert "Backend Engineer" in CATEGORY_SUBCATEGORIES["Software Engineering"]


class TestProcessJobsIntegration:
    """Integration tests for process_jobs with enrichment (require API)."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_enrichment_adds_category(self):
        """Test that enrichment adds category field."""
        import os
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not set")

        jobs = [{"title": "Senior Software Engineer", "company": "TestCo"}]
        results = process_jobs(jobs, enrich=True)

        assert len(results) == 1
        assert "category" in results[0]
        assert results[0]["category"] in ALLOWED_CATEGORIES
