"""Pydantic models for UK Charities MCP server responses."""

from pydantic import BaseModel


class CharityContact(BaseModel):
    """Contact information for a charity."""

    address: str | None = None
    postcode: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None


class Trustee(BaseModel):
    """A charity trustee."""

    name: str


class CharityDetails(BaseModel):
    """Full details for a charity."""

    name: str
    registration_number: int
    charity_type: str | None = None
    status: str
    registration_date: str | None = None
    contact: CharityContact
    trustees: list[Trustee] = []
    causes: list[str] = []
    beneficiaries: list[str] = []
    operations: list[str] = []
    income: int | None = None
    spending: int | None = None


class IncomeBreakdown(BaseModel):
    """Breakdown of charity income by source."""

    donations_and_legacies: int | None = None
    charitable_activities: int | None = None
    other_trading: int | None = None
    investments: int | None = None
    government_grants: int | None = None
    other: int | None = None
    total: int | None = None


class SpendingBreakdown(BaseModel):
    """Breakdown of charity spending by category."""

    charitable_activities: int | None = None
    raising_funds: int | None = None
    governance: int | None = None
    grants_to_institutions: int | None = None
    other: int | None = None
    total: int | None = None


class FinancialYear(BaseModel):
    """Financial data for a single year."""

    year_end: str
    income: IncomeBreakdown
    spending: SpendingBreakdown


class CharityFinancials(BaseModel):
    """Financial information for a charity."""

    name: str
    registration_number: int
    history: list[FinancialYear] = []


class CharityTrustees(BaseModel):
    """Trustees for a charity."""

    name: str
    registration_number: int
    trustees: list[Trustee] = []


class GoverningDocument(BaseModel):
    """Governing document information for a charity."""

    name: str
    registration_number: int
    charitable_objects: str | None = None
    governing_document: str | None = None
    area_of_benefit: str | None = None
