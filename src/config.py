"""Configuration management with validation."""

from __future__ import annotations

from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Annotated

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AmazonRegion(str, Enum):
    """Supported Amazon regions."""

    NL = "nl"
    DE = "de"
    FR = "fr"
    ES = "es"
    IT = "it"
    UK = "co.uk"
    US = "com"

    @property
    def url(self) -> str:
        """Get the Amazon URL for this region."""
        return f"https://www.amazon.{self.value}"

    @property
    def language_hint(self) -> str:
        """Get a language hint for product searches."""
        hints = {
            "nl": "puntenslijper",  # Dutch
            "de": "Anspitzer",  # German
            "fr": "taille-crayon",  # French
            "es": "sacapuntas",  # Spanish
            "it": "temperamatite",  # Italian
            "co.uk": "pencil sharpener",  # English
            "com": "pencil sharpener",  # English
        }
        return hints.get(self.value, "pencil sharpener")


class Settings(BaseSettings):
    """Application settings with environment variable loading."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Amazon credentials
    amazon_nl_username: Annotated[str, Field(description="Amazon account email")]
    amazon_nl_password: Annotated[SecretStr, Field(description="Amazon account password")]

    # Google Gemini API
    google_api_key: Annotated[SecretStr, Field(description="Google Gemini API key")]

    # Shopping configuration
    max_price_eur: Annotated[
        Decimal, Field(default=Decimal("10.00"), description="Maximum price in EUR")
    ] = Decimal("10.00")

    product_search: Annotated[
        str, Field(default="pencil sharpener", description="Product to search for")
    ] = "pencil sharpener"

    region: Annotated[
        AmazonRegion, Field(default=AmazonRegion.NL, description="Amazon region")
    ] = AmazonRegion.NL

    min_rating: Annotated[
        float, Field(default=3.5, ge=0, le=5, description="Minimum product rating")
    ] = 3.5

    # OpenClaw configuration
    openclaw_config: Annotated[
        Path, Field(default=Path("openclaw.json"), description="OpenClaw config file path")
    ] = Path("openclaw.json")

    headless: Annotated[
        bool, Field(default=False, description="Run browser in headless mode")
    ] = False

    @field_validator("max_price_eur", mode="before")
    @classmethod
    def validate_price(cls, v: str | int | float | Decimal) -> Decimal:
        """Validate and convert price to Decimal."""
        if isinstance(v, str):
            v = v.replace(",", ".").replace("€", "").strip()
        return Decimal(str(v))

    @property
    def amazon_url(self) -> str:
        """Get the Amazon URL for the configured region."""
        return self.region.url

    @property
    def search_terms(self) -> list[str]:
        """Get search terms including language-specific alternatives."""
        terms = [self.product_search]
        if self.region.language_hint != self.product_search:
            terms.append(self.region.language_hint)
        return terms


def load_settings() -> Settings:
    """Load and validate settings from environment."""
    return Settings()  # type: ignore[call-arg]
