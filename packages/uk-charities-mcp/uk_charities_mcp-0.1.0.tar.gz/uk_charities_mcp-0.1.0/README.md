# UK Charities MCP Server

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Server-green.svg)](https://modelcontextprotocol.io/)

Query UK charity data directly from Claude using the official Charity Commission API.

> **Why I built this:** MCP integration with UK public sector data APIs. See also: [food-hygiene-mcp](https://github.com/w4sspr/food-hygiene-mcp) for FSA food hygiene ratings.

## Features

Query registered charities with 4 specialized tools:

| Tool | Description |
|------|-------------|
| `get_charity_details` | Full charity info: contact, trustees, causes, finances |
| `get_charity_financials` | 5 years of detailed income & spending breakdowns |
| `get_charity_trustees` | List of current trustees |
| `get_governing_document` | Charitable objects, governing doc, area of benefit |

## Quick Start

1. Get your free API key from [api-portal.charitycommission.gov.uk](https://api-portal.charitycommission.gov.uk/)
2. Add to Claude Desktop config (see below)
3. Restart Claude Desktop
4. Ask: "Get details for Oxfam (charity 202918)"

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

### Option 1: Via PyPI (recommended)

```json
{
  "mcpServers": {
    "uk-charities": {
      "command": "uvx",
      "args": ["uk-charities-mcp"],
      "env": {
        "CCEW_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Option 2: From source

```bash
git clone https://github.com/w4sspr/uk-charities-mcp.git
cd uk-charities-mcp
uv sync
```

```json
{
  "mcpServers": {
    "uk-charities": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/uk-charities-mcp", "uk-charities-mcp"],
      "env": {
        "CCEW_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

> **Note:** If you get `spawn uvx ENOENT` or `spawn uv ENOENT`, use the full path. Run `which uvx` or `which uv` to find it, then use that path in the `command` field.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) package manager
- CCEW API key (free at [api-portal.charitycommission.gov.uk](https://api-portal.charitycommission.gov.uk/))

## Finding Charity Registration Numbers

This MCP requires charity registration numbers. Find them at:
**https://register-of-charities.charitycommission.gov.uk/**

### Example Charities

| Charity | Registration # |
|---------|----------------|
| Oxfam | 202918 |
| British Heart Foundation | 225971 |
| Cancer Research UK | 1089464 |
| RSPCA | 219099 |
| Barnardo's | 216250 |
| Save the Children | 213890 |
| British Red Cross | 220949 |

## Example Prompts

Once connected, try asking Claude:

- "Get details for charity 202918" (Oxfam)
- "Show me the financial history for the British Heart Foundation (225971)"
- "Who are the trustees of Cancer Research UK?"
- "What are the charitable objects of the RSPCA?"

## Development

### Running Tests

```bash
export CCEW_API_KEY=your-api-key
uv run pytest tests/ -v
```

### Testing with MCP Inspector

```bash
CCEW_API_KEY=your-api-key uv run mcp dev src/uk_charities_mcp/server.py
```

## API Details

This server uses the official [Charity Commission API](https://api-portal.charitycommission.gov.uk/), which provides live data from the Register of Charities.

### Tool Specifications

#### get_charity_details

```python
get_charity_details(registration_number: int) -> CharityDetails
```

Returns: name, registration number, charity type, status, registration date, contact info, trustees, causes, beneficiaries, operations, latest income/spending.

#### get_charity_financials

```python
get_charity_financials(registration_number: int) -> CharityFinancials
```

Returns up to 5 years of detailed financial records with breakdowns:
- **Income**: donations & legacies, charitable activities, trading, investments, government grants
- **Spending**: charitable activities, fundraising, governance, grants to institutions

#### get_charity_trustees

```python
get_charity_trustees(registration_number: int) -> CharityTrustees
```

Returns the charity name and list of current trustees.

#### get_governing_document

```python
get_governing_document(registration_number: int) -> GoverningDocument
```

Returns the charity's charitable objects (mission statement), governing document description, and area of benefit.

## Limitations

### What This MCP Cannot Do

| Limitation | Reason |
|------------|--------|
| **Search by name** | CCEW API has no search endpoint. You must provide the registration number. |
| **Scotland charities** | Only covers England & Wales. Scottish charities are regulated by [OSCR](https://www.oscr.org.uk/). |
| **Northern Ireland charities** | Only covers England & Wales. NI charities are regulated by [CCNI](https://www.charitycommissionni.org.uk/). |
| **Sector-wide statistics** | Cannot aggregate across all charities without downloading the full register. |
| **Historical trustees** | API only provides current trustees, not historical records. |

### Prompts That Won't Work

These types of requests require search functionality or aggregation that the API doesn't support:

- "Find mental health charities in London" (no search by cause/location)
- "List the largest charities by income" (no ranking/sorting)
- "How many charities are there in the UK?" (no aggregate stats)
- "Compare Oxfam and Save the Children" (works, but you need both reg numbers)

### Workaround

To find a charity's registration number:
1. Go to [register-of-charities.charitycommission.gov.uk](https://register-of-charities.charitycommission.gov.uk/)
2. Search for the charity by name
3. Copy the registration number from the results
4. Use that number with this MCP

## Roadmap

- [ ] Scotland charities via [OSCR API](https://www.oscr.org.uk/)
- [ ] Northern Ireland charities via [CCNI API](https://www.charitycommissionni.org.uk/)
- [ ] Caching layer to reduce API calls
- [ ] Bulk lookup for comparing multiple charities

## License

MIT
