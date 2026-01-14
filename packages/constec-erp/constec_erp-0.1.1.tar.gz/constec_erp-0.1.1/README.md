# Constec ERP Client

**Fully auto-generated Python client library for the Constec ERP API with perfect IDE autocomplete.**

This library provides type-safe, async-first access to the Constec ERP system for managing customers, suppliers, sellers, and executing custom queries.

## Features

✨ **Fully Auto-Generated** - Always in sync with the API  
🎯 **Perfect Autocomplete** - Full IDE support with type hints  
⚡ **Async-First** - Built with `httpx` for modern async Python  
🔒 **Type-Safe** - Complete Pydantic models for all responses  
📦 **Easy to Use** - Clean, intuitive API wrapper  

## Installation

```bash
pip install constec-erp
```

This automatically installs the base `constec` library as well.

## Quick Start

```python
import asyncio
from uuid import UUID
from constec.erp import ErpClient

async def main():
    async with ErpClient(base_url="https://api.example.com:8001") as client:
        company_id = UUID("your-company-uuid-here")
        
        # Get suppliers with full autocomplete support
        suppliers = await client.get_suppliers(
            company_id=company_id,
            limit=10,
            name="ACME"
        )
        
        print(f"Found {len(suppliers)} suppliers")
        for supplier in suppliers:
            print(f"- {supplier.pro_raz_soc} (CUIT: {supplier.pro_cuit})")

asyncio.run(main())
```

## Why This Library?

### Perfect IDE Autocomplete

When you type `ErpClient(` your IDE shows:
- ✅ `base_url: str` parameter

When you type `client.` you see all methods:
- ✅ `get_suppliers()`
- ✅ `get_customers()`
- ✅ `get_sellers()`

When you type `client.get_suppliers(` you see all parameters with types:
- ✅ `company_id: UUID`
- ✅ `limit: int = 100`
- ✅ `offset: int = 0`
- ✅ `name: Optional[str] = None`
- ✅ `cuit: Optional[str] = None`

When you access results: `suppliers[0].` you see all fields:
- ✅ `pro_raz_soc`
- ✅ `pro_cuit`
- ✅ All supplier fields with proper types

**No `# type: ignore` comments needed anywhere!**

## Usage Examples

### Get Suppliers

```python
from constec.erp import ErpClient

async with ErpClient(base_url="https://api.example.com:8001") as client:
    # Get all suppliers
    suppliers = await client.get_suppliers(
        company_id=company_id,
        limit=100
    )
    
    # Search by name
    suppliers = await client.get_suppliers(
        company_id=company_id,
        name="Distributor",
        limit=20
    )
    
    # Search by CUIT
    suppliers = await client.get_suppliers(
        company_id=company_id,
        cuit="30-12345678-9"
    )
    
    # Pagination
    suppliers = await client.get_suppliers(
        company_id=company_id,
        limit=50,
        offset=100  # Get next page
    )
```

### Get Customers

```python
# Get all customers
customers = await client.get_customers(
    company_id=company_id,
    limit=100
)

# Search by name
customers = await client.get_customers(
    company_id=company_id,
    name="ACME Corp"
)

# Search by CUIT
customers = await client.get_customers(
    company_id=company_id,
    cuit="20-98765432-1"
)

# Access customer data
for customer in customers:
    print(f"Name: {customer.cli_raz_soc}")
    print(f"CUIT: {customer.cli_cuit}")
    print(f"Email: {customer.cli_email}")
```

### Get Sellers

```python
# Get all sellers
sellers = await client.get_sellers(
    company_id=company_id,
    limit=50
)

# Search by name
sellers = await client.get_sellers(
    company_id=company_id,
    name="John"
)

# Access seller data
for seller in sellers:
    print(f"Code: {seller.ven_cod}")
    print(f"Name: {seller.ven_desc}")
    print(f"Active: {seller.ven_activo}")
```

### Error Handling

```python
from constec.shared import ConstecAPIError, ConstecConnectionError

try:
    suppliers = await client.get_suppliers(
        company_id=company_id,
        limit=10
    )
except ConstecConnectionError:
    print("Failed to connect to API")
except ConstecAPIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
```

## Available Data Models

All response objects are fully typed Pydantic models with autocomplete support.

### SupplierSchema

- `pro_cod: str` - Supplier code
- `pro_raz_soc: str | None` - Company name
- `pro_cuit: str | None` - Tax ID (CUIT)
- `pro_email: str | None` - Email address
- `pro_tel: str | None` - Phone number
- `pro_direc: str | None` - Address
- `pro_habilitado: bool | None` - Enabled status
- `pro_fec_mod: datetime | None` - Last modified date

### CustomerSchema

- `cli_cod: str` - Customer code
- `cli_raz_soc: str | None` - Company name
- `cli_nom_fantasia: str | None` - Trade name
- `cli_cuit: str | None` - Tax ID (CUIT)
- `cli_email: str | None` - Email address
- `cli_tel: str | None` - Phone number
- `cli_direc: str | None` - Address
- `cli_loc: str | None` - Location
- `cli_habilitado: bool | None` - Enabled status
- `cli_fec_mod: datetime | None` - Last modified date

### SellerSchema

- `ven_cod: str` - Seller code
- `ven_desc: str | None` - Name/description
- `ven_email: str | None` - Email address
- `ven_tel: str | None` - Phone number
- `ven_activo: bool | None` - Active status
- `ven_fec_mod: datetime | None` - Last modified date

## Connection Parameters

All methods require a `company_id` (UUID) to identify which company's data to access.

```python
from uuid import UUID

company_id = UUID("your-company-uuid-here")

suppliers = await client.get_suppliers(company_id=company_id)
```

## Requirements

- Python 3.9 or higher
- httpx
- pydantic
- attrs

## More Examples

Check the `examples/` directory for complete working examples:

- `basic_usage_easy.py` - Getting started with ErpClient
- `search_customers.py` - Customer search examples
- `pagination.py` - Working with paginated results

## How It Works: Auto-Generation

This library is **100% auto-generated** from the Constec ERP API's OpenAPI specification. This means:

✅ **Zero manual maintenance** - When the API changes, just regenerate  
✅ **Always in sync** - Client matches the API exactly  
✅ **Type-safe** - Full IDE autocomplete and type checking  
✅ **No stale documentation** - Code is the source of truth  

### Two-Layer Architecture

The library uses a smart two-layer approach:

**Layer 1: Low-Level Client** (auto-generated by `openapi-python-client`)
- Located in `constec/erp/client.py`, `api/`, `models/`
- Direct OpenAPI spec translation
- Used internally

**Layer 2: User-Friendly Wrapper** (auto-generated from OpenAPI spec)
- Located in `constec/erp/easy.py`
- Clean, simple API with perfect autocomplete
- **This is what you use!**

### Example: What You Get

```python
from constec.erp import ErpClient  # ← Clean wrapper

async with ErpClient(base_url="...") as client:  # ← Perfect autocomplete
    suppliers = await client.get_suppliers(      # ← Perfect autocomplete
        company_id=uuid,                        # ← Perfect autocomplete
        limit=10,                               # ← Perfect autocomplete
    )
    # Returns clean list[SupplierSchema] - no complex union types!
```

### Regenerating the Client

If you're maintaining this library and the API changes, regenerate with:

```bash
# From the monorepo root (constec-services/)
./tools/ci/generate-erp-client.sh
```

This script:
1. Starts the constec-erp-api server
2. Fetches OpenAPI spec from `/erp/v1/openapi.json`
3. Generates low-level client with `openapi-python-client`
4. Generates user-friendly wrapper (`easy.py`)
5. Creates type stubs (`.pyi`) for IDE support
6. Stops the API server

Everything in `constec/erp/` is auto-generated - **never edit these files manually!**

## Advanced: Using the Low-Level Client

If you need direct access to the low-level auto-generated client:

```python
from constec.erp import Client
from constec.erp.api.suppliers import list_suppliers_erp_v1_suppliers_get

client = Client(base_url="https://api.example.com:8001")

response = await list_suppliers_erp_v1_suppliers_get.asyncio_detailed(
    client=client,
    company_id=company_id,
)

if response.parsed:
    suppliers = response.parsed.items
```

**Note:** The easy wrapper (`ErpClient`) is recommended for most use cases.

## Contributing

This is an auto-generated library. To contribute:

1. Make changes to the **API** (`constec-erp-api`), not this client
2. Update the OpenAPI spec in the API
3. Regenerate this client with `./tools/ci/generate-erp-client.sh`
4. Test the changes
5. Submit a PR

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
- Check the `examples/` directory
- Review the auto-generated models in `constec/erp/models/`
- Check API documentation at your API server's `/erp/v1/docs`

---

**Generated from OpenAPI spec** - This README documents the current auto-generated client.
