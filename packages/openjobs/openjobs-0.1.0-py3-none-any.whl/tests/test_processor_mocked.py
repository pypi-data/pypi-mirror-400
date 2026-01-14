"""Mocked tests for openjobs.processor module - no live API required."""

import pytest
from unittest.mock import patch, MagicMock

from openjobs.processor import (
    process_job,
    process_jobs,
    classify_job,
    enhance_job_output,
    _call_gemini,
    RateLimiter,
    ALLOWED_CATEGORIES,
    ALLOWED_TECH_STACKS,
)


class TestRateLimiterProcessor:
    """Tests for processor's RateLimiter."""

    def test_rate_limiter_creation(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(requests_per_minute=60)
        assert limiter.requests_per_minute == 60


class TestCallGeminiMocked:
    """Mocked tests for _call_gemini."""

    @patch('openjobs.processor.requests.post')
    @patch('openjobs.processor.gemini_rate_limiter')
    def test_successful_call(self, mock_limiter, mock_post):
        """Test successful Gemini API call."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': '{"category": "Software Engineering"}'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response

        result = _call_gemini('Test prompt', api_key='test-key')

        assert result == {'category': 'Software Engineering'}

    @patch('openjobs.processor.requests.post')
    @patch('openjobs.processor.gemini_rate_limiter')
    def test_call_with_markdown_response(self, mock_limiter, mock_post):
        """Test handling of markdown-wrapped JSON response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': '```json\n{"result": "value"}\n```'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response

        result = _call_gemini('Test prompt', api_key='test-key')

        assert result == {'result': 'value'}

    @patch('openjobs.processor.requests.post')
    @patch('openjobs.processor.gemini_rate_limiter')
    def test_call_api_error(self, mock_limiter, mock_post):
        """Test handling of API error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Server Error'
        mock_post.return_value = mock_response

        result = _call_gemini('Test prompt', api_key='test-key')

        assert result is None

    def test_call_no_api_key(self):
        """Test call fails without API key."""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': ''}):
            result = _call_gemini('Test prompt')
            assert result is None

    @patch('openjobs.processor.requests.post')
    @patch('openjobs.processor.gemini_rate_limiter')
    def test_call_invalid_json(self, mock_limiter, mock_post):
        """Test handling of invalid JSON response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': 'Not valid JSON at all'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response

        result = _call_gemini('Test prompt', api_key='test-key')

        assert result is None

    @patch('openjobs.processor.requests.post')
    @patch('openjobs.processor.gemini_rate_limiter')
    def test_call_empty_candidates(self, mock_limiter, mock_post):
        """Test handling of empty candidates."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'candidates': []}
        mock_post.return_value = mock_response

        result = _call_gemini('Test prompt', api_key='test-key')

        assert result is None


class TestClassifyJobMocked:
    """Mocked tests for classify_job."""

    @patch('openjobs.processor._call_gemini')
    def test_successful_classification(self, mock_gemini):
        """Test successful job classification."""
        mock_gemini.return_value = {
            'category': 'Software Engineering',
            'subcategory': 'Backend Engineer',
            'similar_job_title': 'Software Engineer'
        }

        result = classify_job('Senior Backend Engineer')

        assert result['category'] == 'Software Engineering'
        assert result['subcategory'] == 'Backend Engineer'

    @patch('openjobs.processor._call_gemini')
    def test_classification_api_failure(self, mock_gemini):
        """Test classification when API fails."""
        mock_gemini.return_value = None

        result = classify_job('Engineer')

        assert result['category'] == 'No Match Found'
        assert result['subcategory'] == 'No Match Found'

    @patch('openjobs.processor._call_gemini')
    def test_classification_invalid_category(self, mock_gemini):
        """Test classification with invalid category gets corrected."""
        mock_gemini.return_value = {
            'category': 'Invalid Category',
            'subcategory': 'Something',
            'similar_job_title': 'Engineer'
        }

        result = classify_job('Engineer')

        assert result['category'] == 'No Match Found'


class TestEnhanceJobOutputMocked:
    """Mocked tests for enhance_job_output."""

    @patch('openjobs.processor._call_gemini')
    def test_successful_enhancement(self, mock_gemini):
        """Test successful job enhancement."""
        mock_gemini.return_value = {
            'simplified_job_title': 'Software Engineer',
            'tech_stack': ['Python', 'AWS'],
            'experience_required': '3-5 years',
            'salary_range': '$100,000 - $150,000',
            'remote_type': 'Remote',
            'contract_type': 'Full-Time'
        }

        result = enhance_job_output('Senior Software Engineer', 'Job description here')

        assert result['simplified_job_title'] == 'Software Engineer'
        assert 'Python' in result['tech_stack']
        assert result['contract_type'] == 'Full-Time'

    @patch('openjobs.processor._call_gemini')
    def test_enhancement_api_failure(self, mock_gemini):
        """Test enhancement when API fails returns defaults."""
        mock_gemini.return_value = None

        result = enhance_job_output('Engineer', 'Description')

        assert result['simplified_job_title'] == 'Engineer'
        assert result['tech_stack'] == []
        assert result['salary_range'] == 'Not Specified'

    @patch('openjobs.processor._call_gemini')
    def test_enhancement_filters_invalid_tech(self, mock_gemini):
        """Test that invalid tech stack items are filtered."""
        mock_gemini.return_value = {
            'tech_stack': ['Python', 'InvalidTech', 'AWS', 'FakeTech'],
            'contract_type': 'Full-Time'
        }

        result = enhance_job_output('Engineer', 'Description')

        # Only valid tech should remain
        assert 'Python' in result.get('tech_stack', [])
        assert 'InvalidTech' not in result.get('tech_stack', [])

    @patch('openjobs.processor._call_gemini')
    def test_enhancement_invalid_contract_type(self, mock_gemini):
        """Test that invalid contract type gets corrected."""
        mock_gemini.return_value = {
            'contract_type': 'InvalidType'
        }

        result = enhance_job_output('Engineer', 'Description')

        assert result['contract_type'] == 'Other'


class TestProcessJobMocked:
    """Mocked tests for process_job with enrichment."""

    @patch('openjobs.processor.enhance_job_output')
    @patch('openjobs.processor.classify_job')
    def test_full_processing_with_enrichment(self, mock_classify, mock_enhance):
        """Test full job processing with enrichment."""
        mock_classify.return_value = {
            'category': 'Software Engineering',
            'subcategory': 'Backend Engineer',
            'similar_job_title': 'Engineer'
        }
        mock_enhance.return_value = {
            'simplified_job_title': 'Engineer',
            'tech_stack': ['Python'],
            'experience_required': '3 years',
            'education_level': "Bachelor's",
            'salary_range': '$100k',
            'remote_type': 'Remote',
            'contract_type': 'Full-Time',
            'benefits': ['Health'],
            'requirements': ['Python']
        }

        job = {
            'title': 'Senior Backend Engineer',
            'company': 'TestCo',
            'description': 'We are looking for...',
            'location': 'Remote'
        }

        result = process_job(job, enrich=True, api_key='test-key')

        assert result['category'] == 'Software Engineering'
        assert result['title_original'] == 'Senior Backend Engineer'
        assert 'tech_stack' in result

    @patch('openjobs.processor.classify_job')
    def test_processing_without_description(self, mock_classify):
        """Test processing job without description."""
        mock_classify.return_value = {
            'category': 'Software Engineering',
            'subcategory': 'Backend Engineer',
            'similar_job_title': 'Engineer'
        }

        job = {'title': 'Engineer', 'company': 'TestCo'}

        result = process_job(job, enrich=True, api_key='test-key')

        assert result['category'] == 'Software Engineering'
        # Should use similar_job_title as simplified
        assert 'title_simplified' in result


class TestProcessJobsMocked:
    """Mocked tests for process_jobs with filtering."""

    @patch('openjobs.processor.classify_job')
    def test_category_filtering(self, mock_classify):
        """Test filtering jobs by category."""
        # First job: Software Engineering
        # Second job: Marketing
        mock_classify.side_effect = [
            {'category': 'Software Engineering', 'subcategory': 'Backend', 'similar_job_title': 'Eng'},
            {'category': 'Marketing', 'subcategory': 'Growth', 'similar_job_title': 'Marketer'},
            {'category': 'Software Engineering', 'subcategory': 'Frontend', 'similar_job_title': 'Eng'},
        ]

        jobs = [
            {'title': 'Backend Engineer', 'company': 'A'},
            {'title': 'Marketing Manager', 'company': 'B'},
            {'title': 'Frontend Engineer', 'company': 'C'},
        ]

        result = process_jobs(
            jobs,
            enrich=True,
            api_key='test-key',
            filter_categories=['Software Engineering']
        )

        assert len(result) == 2
        assert all(j['category'] == 'Software Engineering' for j in result)

    @patch('openjobs.processor.classify_job')
    def test_multiple_category_filter(self, mock_classify):
        """Test filtering with multiple categories."""
        mock_classify.side_effect = [
            {'category': 'Software Engineering', 'subcategory': 'Backend', 'similar_job_title': 'Eng'},
            {'category': 'Data', 'subcategory': 'ML', 'similar_job_title': 'DS'},
            {'category': 'Marketing', 'subcategory': 'Growth', 'similar_job_title': 'Marketer'},
        ]

        jobs = [
            {'title': 'Engineer', 'company': 'A'},
            {'title': 'Data Scientist', 'company': 'B'},
            {'title': 'Marketer', 'company': 'C'},
        ]

        result = process_jobs(
            jobs,
            enrich=True,
            api_key='test-key',
            filter_categories=['Software Engineering', 'Data']
        )

        assert len(result) == 2
