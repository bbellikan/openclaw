"""Tests for configuration management."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.config import AmazonRegion, Settings


class TestAmazonRegion:
    """Tests for AmazonRegion enum."""

    def test_url_generation(self) -> None:
        """Test URL generation for each region."""
        assert AmazonRegion.NL.url == "https://www.amazon.nl"
        assert AmazonRegion.DE.url == "https://www.amazon.de"
        assert AmazonRegion.UK.url == "https://www.amazon.co.uk"
        assert AmazonRegion.US.url == "https://www.amazon.com"

    def test_language_hints(self) -> None:
        """Test language-specific search hints."""
        assert AmazonRegion.NL.language_hint == "puntenslijper"
        assert AmazonRegion.DE.language_hint == "Anspitzer"
        assert AmazonRegion.FR.language_hint == "taille-crayon"
        assert AmazonRegion.US.language_hint == "pencil sharpener"


class TestSettings:
    """Tests for Settings configuration."""

    def test_price_validation_string(self) -> None:
        """Test price validation from string input."""
        settings = Settings(
            amazon_nl_username="test@example.com",
            amazon_nl_password="password123",
            google_api_key="test-key",
            max_price_eur="15.50",
        )
        assert settings.max_price_eur == Decimal("15.50")

    def test_price_validation_with_currency(self) -> None:
        """Test price validation with currency symbol."""
        settings = Settings(
            amazon_nl_username="test@example.com",
            amazon_nl_password="password123",
            google_api_key="test-key",
            max_price_eur="€20,00",
        )
        assert settings.max_price_eur == Decimal("20.00")

    def test_search_terms_includes_language_hint(self) -> None:
        """Test that search terms include language-specific alternatives."""
        settings = Settings(
            amazon_nl_username="test@example.com",
            amazon_nl_password="password123",
            google_api_key="test-key",
            region=AmazonRegion.NL,
        )
        terms = settings.search_terms
        assert "pencil sharpener" in terms
        assert "puntenslijper" in terms

    def test_min_rating_bounds(self) -> None:
        """Test that min_rating is validated within bounds."""
        with pytest.raises(ValidationError):
            Settings(
                amazon_nl_username="test@example.com",
                amazon_nl_password="password123",
                google_api_key="test-key",
                min_rating=6.0,  # Invalid: > 5
            )
