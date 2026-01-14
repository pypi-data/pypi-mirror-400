# NCBI E-utilities MCP Server

A Machine Capability Protocol (MCP) server for accessing NCBI E-utilities API. This package provides programmatic access to NCBI databases including PubMed, Protein, Nucleotide, and more.

## Features

- **EInfo**: Get list of Entrez databases or statistics for a specific database
- **ESearch**: Text-based search to retrieve UID lists from NCBI databases
- **ESummary**: Retrieve document summaries (DocSum) for UIDs
- **EFetch**: Fetch full formatted records for UIDs (core functionality)

## Installation

```bash
pip install ncbi-mcp
```

## Configuration

Create a `.env` file in your project root with the following variables:

```env
API_KEY=your_ncbi_api_key  # Optional but recommended for higher rate limits
BASE_URL=https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
```

**Note**: Without an API key, your requests are limited to 3 requests per second. With an API key, you can make up to 10 requests per second.

### Getting an NCBI API Key

To get an NCBI API key, you need to:

1. Register for an NCBI account at [https://www.ncbi.nlm.nih.gov/account/](https://www.ncbi.nlm.nih.gov/account/)
2. Go to your account "Settings" page
3. Find the "API Key Management" area and click "Create an API Key"
4. Copy the generated key and use it in your `.env` file

For more information about NCBI API keys, visit: [https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)

## Usage

The server implements the MCP protocol and can be integrated with MCP-compatible clients.

## Tools Available

### EInfo
- Description: Query NCBI databases, get database statistics
- Parameters: db_name (optional), retmode (default: xml)

### ESearch
- Description: Search for content by term in specified database
- Parameters: db_name (default: pubmed), term (search query)

### ESummary
- Description: Get summary information for specified IDs
- Parameters: db_name (default: pubmed), ids (list of IDs)

### EFetch
- Description: Get complete records for specified IDs
- Parameters: db_name (default: pubmed), ids (list of IDs), retmode (default: xml), rettype (default: abstract)

## Requirements

- Python >= 3.8
- NCBI API key (recommended for higher rate limits)

## License

MIT