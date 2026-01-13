# Pydantic Invoices

Type-safe Pydantic schemas and repository interfaces for invoice management systems.

## Installation

```bash
pip install pydantic-invoices
# or
uv add pydantic-invoices
```

## Usage

### Using Schemas


```python
from pydantic_invoices import Invoice, InvoiceCreate, Client, ClientCreate
from pydantic_invoices.schemas import InvoiceStatus, InvoiceType
from datetime import datetime

# Create invoice data
invoice_data = InvoiceCreate(
    number="INV-001",
    client_id=1,
    company_id=1,
    issue_date=datetime.now(),
    due_date=datetime.now(),
    status=InvoiceStatus.DRAFT,
    type=InvoiceType.STANDARD,
    payment_terms="Net 30",
    lines=[],
)

# Validate and use
invoice = Invoice(id=1, **invoice_data.model_dump())
```

### Invoice Statuses & Types
The library supports a strict state machine workflow:
- **Statuses**: `DRAFT`, `SENT`, `PAID`, `PARTIALLY_PAID`, `CANCELLED`, `REFUNDED`, `CREDITED`.
- **Types**: `STANDARD`, `CREDIT_NOTE`.
- **Linking**: `Credit Notes` can be linked to original invoices via `original_invoice_id`.

### Implementing Repository Interfaces

```python
from pydantic_invoices.interfaces import InvoiceRepository, ClientRepository
from pydantic_invoices import Invoice, InvoiceCreate, Client

class MyInvoiceRepo(InvoiceRepository):
    def create(self, entity: InvoiceCreate) -> Invoice:
        # Your implementation
        pass
    
    def get_by_id(self, id: int) -> Invoice | None:
        # Your implementation
        pass
    
    # ... implement other methods
```

## Architecture

See [System Diagram](docs/system_diagram.md) for a visual overview of the entities and their relationships.

## Features

- ✅ Type-safe Pydantic v2 schemas
- ✅ Repository pattern interfaces
- ✅ No implementation dependencies
- ✅ Fully typed with mypy support
- ✅ Clean separation of concerns
- ✅ Support for **Credit Notes** and **Strict Lifecycle**


## Schemas Included

- `Invoice`, `InvoiceCreate`, `InvoiceUpdate`
- `InvoiceLine`, `InvoiceLineCreate`
- `Client`, `ClientCreate`, `ClientUpdate`
- `Payment`, `PaymentCreate`
- `Company`, `CompanyCreate`, `CompanyUpdate`
- `Product`, `ProductCreate`, `ProductUpdate`
- `PaymentNote`, `PaymentNoteCreate`, `PaymentNoteUpdate`
- `AuditLog`

## Interfaces Included

- `BaseRepository` - Generic CRUD operations
- `InvoiceRepository` - Invoice-specific operations
- `ClientRepository` - Client management
- `PaymentRepository` - Payment tracking
- `CompanyRepository` - Company management
- `ProductRepository` - Product catalog
- `PaymentNoteRepository` - Payment instructions

## License

MIT
