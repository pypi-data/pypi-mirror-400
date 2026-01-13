"""Tests for company enrichment module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ccda_cli.enrichment.company import CompanyEnricher


class TestCompanyEnricher:
    """Test CompanyEnricher class."""

    @pytest.fixture
    def mock_config(self):
        """Mock config."""
        with patch("ccda_cli.enrichment.company.get_config") as mock:
            config = MagicMock()
            config.github.enrich_company_affiliation = True
            config.company_mappings.email_domains = {
                "google.com": "Google",
                "microsoft.com": "Microsoft",
            }
            config.company_mappings.github_companies = {
                "@google": "Google",
                "@microsoft": "Microsoft",
                "Independent": "Independent",
            }
            mock.return_value = config
            yield mock

    def test_is_enabled_with_token(self, mock_config):
        """Enrichment should be enabled when token is provided."""
        enricher = CompanyEnricher(github_token="test_token")
        assert enricher.is_enabled() is True

    def test_is_enabled_without_token(self, mock_config):
        """Enrichment should be disabled without token."""
        enricher = CompanyEnricher(github_token=None)
        assert enricher.is_enabled() is False

    def test_is_enabled_config_disabled(self, mock_config):
        """Enrichment should be disabled if config says so."""
        mock_config.return_value.github.enrich_company_affiliation = False
        enricher = CompanyEnricher(github_token="test_token")
        assert enricher.is_enabled() is False

    def test_extract_username_standard_noreply(self, mock_config):
        """Should extract username from standard noreply email."""
        enricher = CompanyEnricher()
        username = enricher._extract_username("octocat@users.noreply.github.com")
        assert username == "octocat"

    def test_extract_username_numeric_noreply(self, mock_config):
        """Should extract username from numeric noreply email."""
        enricher = CompanyEnricher()
        username = enricher._extract_username("12345+octocat@users.noreply.github.com")
        assert username == "octocat"

    def test_extract_username_non_github(self, mock_config):
        """Should return None for non-GitHub emails."""
        enricher = CompanyEnricher()
        username = enricher._extract_username("user@example.com")
        assert username is None

    def test_get_company_from_email_domain_noreply(self, mock_config):
        """Noreply emails should return Independent."""
        enricher = CompanyEnricher()
        company = enricher._get_company_from_email_domain("user@users.noreply.github.com")
        assert company == "Independent"

    def test_get_company_from_email_domain_mapped(self, mock_config):
        """Should map known domains to companies."""
        enricher = CompanyEnricher()
        company = enricher._get_company_from_email_domain("user@google.com")
        assert company == "Google"

    def test_get_company_from_email_domain_unmapped(self, mock_config):
        """Unknown domains should return Independent."""
        enricher = CompanyEnricher()
        company = enricher._get_company_from_email_domain("user@example.com")
        assert company == "Independent"

    def test_normalize_company_empty(self, mock_config):
        """Empty company should return Independent."""
        enricher = CompanyEnricher()
        assert enricher._normalize_company(None) == "Independent"
        assert enricher._normalize_company("") == "Independent"
        assert enricher._normalize_company("   ") == "Independent"

    def test_normalize_company_with_mapping(self, mock_config):
        """Should normalize company using mappings."""
        enricher = CompanyEnricher()
        company = enricher._normalize_company("Working at @google")
        assert company == "Google"

    def test_normalize_company_no_mapping(self, mock_config):
        """Should return company as-is if no mapping found."""
        enricher = CompanyEnricher()
        company = enricher._normalize_company("Acme Corp")
        assert company == "Acme Corp"

    def test_get_company_without_enrichment(self, mock_config):
        """Should fall back to email domain when enrichment disabled."""
        enricher = CompanyEnricher(github_token=None)
        company = enricher.get_company("user@google.com")
        assert company == "Google"

    def test_get_company_fallback_to_email_domain(self, mock_config):
        """Should use enricher which falls back to email domain."""
        enricher = CompanyEnricher(github_token=None)
        company = enricher.get_company("user@google.com")
        assert company == "Google"

        # Noreply should be independent
        company = enricher.get_company("user@users.noreply.github.com")
        assert company == "Independent"

    @pytest.mark.asyncio
    async def test_enrich_contributors_disabled(self, mock_config):
        """Should do nothing when enrichment is disabled."""
        enricher = CompanyEnricher(github_token=None)
        contributors = {
            "user@example.com": {"name": "User", "company": "Independent"}
        }

        await enricher.enrich_contributors(contributors)

        # Should not modify contributors
        assert contributors["user@example.com"]["company"] == "Independent"

    @pytest.mark.asyncio
    async def test_enrich_contributors_with_cache(self, mock_config):
        """Should use cached profiles."""
        mock_cache = MagicMock()
        mock_cache.get_user_profile.return_value = MagicMock(
            data={"company": "@google"}
        )

        enricher = CompanyEnricher(github_token="test_token", cache=mock_cache)
        contributors = {
            "octocat@users.noreply.github.com": {
                "name": "Octocat",
                "company": "Independent",
            }
        }

        await enricher.enrich_contributors(contributors)

        # Should update from cache
        assert contributors["octocat@users.noreply.github.com"]["company"] == "Google"
