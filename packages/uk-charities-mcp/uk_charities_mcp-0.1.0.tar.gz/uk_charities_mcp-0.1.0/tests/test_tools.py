"""Smoke tests for UK Charities MCP tools.

Tests require the CCEW API to be accessible and
the CCEW_API_KEY environment variable to be set.
"""

import os

import pytest

# Skip all tests if no API key
pytestmark = pytest.mark.skipif(
    not os.environ.get("CCEW_API_KEY"),
    reason="CCEW_API_KEY not set",
)

# Oxfam's registration number - a well-known charity for testing
OXFAM_REG_NUMBER = 202918


@pytest.mark.asyncio
async def test_get_charity_details() -> None:
    """Test getting charity details."""
    from uk_charities_mcp.server import get_charity_details

    details = await get_charity_details(OXFAM_REG_NUMBER)

    assert details.name == "OXFAM"
    assert details.registration_number == OXFAM_REG_NUMBER
    assert details.status == "Registered"
    assert details.charity_type == "Charitable company"
    assert len(details.trustees) > 0
    assert len(details.causes) > 0
    assert details.income is not None
    assert details.income > 0


@pytest.mark.asyncio
async def test_get_charity_financials() -> None:
    """Test getting charity financials."""
    from uk_charities_mcp.server import get_charity_financials

    financials = await get_charity_financials(OXFAM_REG_NUMBER)

    assert financials.name == "OXFAM"
    assert financials.registration_number == OXFAM_REG_NUMBER
    assert len(financials.history) > 0

    # Check first year has data
    latest = financials.history[0]
    assert latest.year_end is not None
    assert latest.income.total is not None
    assert latest.income.total > 0
    assert latest.spending.total is not None


@pytest.mark.asyncio
async def test_get_charity_trustees() -> None:
    """Test getting charity trustees."""
    from uk_charities_mcp.server import get_charity_trustees

    trustees = await get_charity_trustees(OXFAM_REG_NUMBER)

    assert trustees.name == "OXFAM"
    assert trustees.registration_number == OXFAM_REG_NUMBER
    assert len(trustees.trustees) > 0
    assert all(t.name for t in trustees.trustees)


@pytest.mark.asyncio
async def test_get_governing_document() -> None:
    """Test getting governing document info."""
    from uk_charities_mcp.server import get_governing_document

    doc = await get_governing_document(OXFAM_REG_NUMBER)

    assert doc.name == "OXFAM"
    assert doc.registration_number == OXFAM_REG_NUMBER
    assert doc.charitable_objects is not None
    assert "poverty" in doc.charitable_objects.lower()
    assert doc.area_of_benefit is not None


@pytest.mark.asyncio
async def test_charity_not_found() -> None:
    """Test error handling for non-existent charity."""
    from uk_charities_mcp.client import CCEWError
    from uk_charities_mcp.server import get_charity_details

    with pytest.raises(CCEWError):
        await get_charity_details(999999999)
