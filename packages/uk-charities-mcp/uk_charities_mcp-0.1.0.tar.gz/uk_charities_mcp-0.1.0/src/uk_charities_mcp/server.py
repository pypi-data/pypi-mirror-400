"""UK Charities MCP Server.

Query registered charities in England & Wales via the official Charity Commission API.
"""

from mcp.server.fastmcp import FastMCP

from uk_charities_mcp.client import CCEWClient
from uk_charities_mcp.models import (
    CharityContact,
    CharityDetails,
    CharityFinancials,
    CharityTrustees,
    FinancialYear,
    GoverningDocument,
    IncomeBreakdown,
    SpendingBreakdown,
    Trustee,
)

mcp = FastMCP(
    "UK Charities",
    instructions=(
        "Query UK Charity Commission data for registered charities in England & Wales. "
        "Tools require charity registration numbers. Find registration numbers at: "
        "https://register-of-charities.charitycommission.gov.uk/"
    ),
)


def _safe_int(value: float | int | None) -> int | None:
    """Convert a numeric value to int, handling None."""
    if value is None:
        return None
    return int(value)


def _parse_status(reg_status: str | None) -> str:
    """Parse registration status code to human-readable string."""
    status_map = {
        "R": "Registered",
        "RM": "Removed",
    }
    return status_map.get(reg_status or "", reg_status or "Unknown")


def _parse_classifications(who_what_where: list[dict]) -> tuple[list[str], list[str], list[str]]:
    """Parse classifications into causes, beneficiaries, and operations."""
    causes = []
    beneficiaries = []
    operations = []

    for item in who_what_where or []:
        desc = item.get("classification_desc", "")
        class_type = item.get("classification_type", "")

        if class_type == "What":
            causes.append(desc)
        elif class_type == "Who":
            beneficiaries.append(desc)
        elif class_type == "How":
            operations.append(desc)

    return causes, beneficiaries, operations


@mcp.tool()
async def get_charity_details(registration_number: int) -> CharityDetails:
    """Get full details for a UK charity by registration number.

    Args:
        registration_number: The charity's registration number (e.g., 202918 for Oxfam).
            Find registration numbers at: https://register-of-charities.charitycommission.gov.uk/

    Returns:
        Comprehensive charity information including contact details, trustees, and finances.
    """
    async with CCEWClient() as client:
        data = await client.get_charity_details(registration_number)

    # Build address from parts
    address_parts = [
        data.get("address_line_one"),
        data.get("address_line_two"),
        data.get("address_line_three"),
        data.get("address_line_four"),
        data.get("address_line_five"),
    ]
    address = ", ".join(p for p in address_parts if p)

    # Parse trustees
    trustees = [
        Trustee(name=t.get("trustee_name", "Unknown"))
        for t in data.get("trustee_names", [])
        if t.get("trustee_name")
    ]

    # Parse classifications
    causes, beneficiaries, operations = _parse_classifications(data.get("who_what_where", []))

    # Parse registration date
    reg_date = data.get("date_of_registration")
    if reg_date:
        reg_date = reg_date.split("T")[0]  # Remove time portion

    return CharityDetails(
        name=data.get("charity_name", "Unknown"),
        registration_number=data.get("reg_charity_number", registration_number),
        charity_type=data.get("charity_type"),
        status=_parse_status(data.get("reg_status")),
        registration_date=reg_date,
        contact=CharityContact(
            address=address or None,
            postcode=data.get("address_post_code"),
            phone=data.get("phone"),
            email=data.get("email"),
            website=data.get("web"),
        ),
        trustees=trustees,
        causes=causes,
        beneficiaries=beneficiaries,
        operations=operations,
        income=_safe_int(data.get("latest_income")),
        spending=_safe_int(data.get("latest_expenditure")),
    )


@mcp.tool()
async def get_charity_financials(registration_number: int) -> CharityFinancials:
    """Get detailed financial history for a charity.

    Args:
        registration_number: The charity's registration number.

    Returns:
        Up to 5 years of financial data with detailed income and spending breakdowns.
    """
    async with CCEWClient() as client:
        # Get charity name from details
        details = await client.get_charity_details(registration_number)
        name = details.get("charity_name", "Unknown")

        # Get financial history
        history_data = await client.get_financial_history(registration_number)

    history = []
    for record in history_data:
        year_end = record.get("financial_period_end_date", "")
        if year_end:
            year_end = year_end.split("T")[0]

        history.append(
            FinancialYear(
                year_end=year_end,
                income=IncomeBreakdown(
                    donations_and_legacies=_safe_int(record.get("inc_donations_and_legacies")),
                    charitable_activities=_safe_int(record.get("inc_charitable_activities")),
                    other_trading=_safe_int(record.get("inc_other_trading_activities")),
                    investments=_safe_int(record.get("inc_investment")),
                    government_grants=_safe_int(record.get("income_from_govt_grants")),
                    other=_safe_int(record.get("inc_other")),
                    total=_safe_int(record.get("income")),
                ),
                spending=SpendingBreakdown(
                    charitable_activities=_safe_int(record.get("exp_charitable_activities")),
                    raising_funds=_safe_int(record.get("exp_raising_funds")),
                    governance=_safe_int(record.get("exp_governance")),
                    grants_to_institutions=_safe_int(record.get("exp_grants_institution")),
                    other=_safe_int(record.get("exp_other")),
                    total=_safe_int(record.get("expenditure")),
                ),
            )
        )

    return CharityFinancials(
        name=name,
        registration_number=registration_number,
        history=history,
    )


@mcp.tool()
async def get_charity_trustees(registration_number: int) -> CharityTrustees:
    """Get the list of trustees for a charity.

    Args:
        registration_number: The charity's registration number.

    Returns:
        The charity name and list of current trustees.
    """
    async with CCEWClient() as client:
        data = await client.get_charity_details(registration_number)

    trustees = [
        Trustee(name=t.get("trustee_name", "Unknown"))
        for t in data.get("trustee_names", [])
        if t.get("trustee_name")
    ]

    return CharityTrustees(
        name=data.get("charity_name", "Unknown"),
        registration_number=data.get("reg_charity_number", registration_number),
        trustees=trustees,
    )


@mcp.tool()
async def get_governing_document(registration_number: int) -> GoverningDocument:
    """Get the charitable objects and governing document for a charity.

    Args:
        registration_number: The charity's registration number.

    Returns:
        The charity's charitable objects (mission statement), governing document type,
        and area of benefit.
    """
    async with CCEWClient() as client:
        # Get charity name from details
        details = await client.get_charity_details(registration_number)
        name = details.get("charity_name", "Unknown")

        # Get governing document
        data = await client.get_governing_document(registration_number)

    return GoverningDocument(
        name=name,
        registration_number=registration_number,
        charitable_objects=data.get("charitable_objects"),
        governing_document=data.get("governing_document_description"),
        area_of_benefit=data.get("area_of_benefit"),
    )


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
