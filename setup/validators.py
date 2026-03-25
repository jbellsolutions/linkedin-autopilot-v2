"""Simple input validators for the setup wizard."""


def validate_email(value: str) -> bool:
    """Basic email validation - checks for @ symbol and domain."""
    if not value or "@" not in value:
        return False
    parts = value.split("@")
    if len(parts) != 2:
        return False
    local, domain = parts
    return len(local) > 0 and "." in domain and len(domain) > 2


def validate_url(value: str) -> bool:
    """Check that value starts with http:// or https://."""
    if not value:
        return False
    return value.startswith("http://") or value.startswith("https://")


def validate_linkedin_url(value: str) -> bool:
    """Check that value is a LinkedIn URL."""
    if not value:
        return False
    return "linkedin.com" in value.lower()


def validate_api_key(value: str) -> bool:
    """Check that API key is non-empty and reasonably long."""
    if not value:
        return False
    return len(value.strip()) > 10
