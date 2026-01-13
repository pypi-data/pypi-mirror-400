"""Invoice schemas - Pure Pydantic models."""

from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, computed_field
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING



class InvoiceStatus(str, Enum):
    """Valid invoice status values."""
    DRAFT = "DRAFT"
    SENT = "SENT"
    UNPAID = "UNPAID"  # Legacy/Simple flow
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    CREDITED = "CREDITED"


class InvoiceType(str, Enum):
    """Type of invoice document."""
    STANDARD = "STANDARD"
    CREDIT_NOTE = "CREDIT_NOTE"


if TYPE_CHECKING:
    from .invoice_line import InvoiceLine, InvoiceLineCreate
    from .payment import Payment
    from .audit_log import AuditLog


class InvoiceBase(BaseModel):
    """Base invoice schema."""

    number: str = Field(
        ..., min_length=1, max_length=50, description="Unique invoice number"
    )
    issue_date: datetime = Field(
        default_factory=datetime.now, description="Invoice issue date"
    )
    status: InvoiceStatus = Field(
        default=InvoiceStatus.DRAFT,
        description="Invoice payment status",
    )
    type: InvoiceType = Field(
        default=InvoiceType.STANDARD,
        description="Type of invoice (Standard or Credit Note)",
    )
    due_date: Optional[date] = Field(None, description="Payment due date")
    payment_terms: str = Field(
        default="Net 30",
        max_length=100,
        description="Payment terms (e.g., Net 30, Net 60)",
    )

    # linking
    original_invoice_id: Optional[int] = Field(
        None, description="ID of the original invoice (for Credit Notes)"
    )
    reason: Optional[str] = Field(
        None, max_length=500, description="Reason for credit note or cancellation"
    )

    # Company (defaults to company #1)
    company_id: int = Field(
        default=1, gt=0, description="Company that issues this invoice"
    )

    # Client snapshots (immutable)
    client_name_snapshot: Optional[str] = Field(
        None, max_length=255, description="Client name at invoice time"
    )
    client_address_snapshot: Optional[str] = Field(
        None, max_length=500, description="Client address at invoice time"
    )
    client_tax_id_snapshot: Optional[str] = Field(
        None, max_length=50, description="Client tax ID at invoice time"
    )

    # Payment notes (can select multiple)
    payment_note_ids: List[int] = Field(
        default_factory=list, description="IDs of payment notes to include"
    )


class InvoiceCreate(InvoiceBase):
    """Schema for creating an invoice."""

    client_id: int = Field(..., description="Client ID")
    lines: List["InvoiceLineCreate"] = Field(default_factory=list)
    status: InvoiceStatus = Field(
        default=InvoiceStatus.DRAFT,  # Default to DRAFT when creating
        description="Invoice payment status",
    )


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice."""

    status: Optional[InvoiceStatus] = None
    due_date: Optional[date] = None
    payment_terms: Optional[str] = Field(None, max_length=100)
    reason: Optional[str] = Field(None, max_length=500)



class Invoice(InvoiceBase):
    """Complete invoice schema with computed properties."""

    id: int
    company_id: int  # Required
    client_id: int
    type: InvoiceType = Field(default=InvoiceType.STANDARD)
    original_invoice_id: Optional[int] = None
    reason: Optional[str] = None
    lines: List["InvoiceLine"] = Field(default_factory=list)
    payments: List["Payment"] = Field(default_factory=list)
    audit_logs: List["AuditLog"] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_amount(self) -> float:
        """Calculate total amount from all line items."""
        return sum(line.total for line in self.lines)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_paid(self) -> float:
        """Calculate total amount paid across all payments."""
        return sum(payment.amount for payment in self.payments)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def balance_due(self) -> float:
        """Calculate remaining balance to be paid."""
        return self.total_amount - self.total_paid

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_overdue(self) -> bool:
        """Check if invoice is past due date."""
        if self.status in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED, InvoiceStatus.CREDITED):
            return False
        if self.due_date:
            return date.today() > self.due_date
        return False

    @computed_field  # type: ignore[prop-decorator]
    @property
    def days_overdue(self) -> int:
        """Calculate number of days past due."""
        if not self.is_overdue or self.due_date is None:
            return 0
        return (date.today() - self.due_date).days

    model_config = ConfigDict(from_attributes=True)


# Resolve forward references after all classes are defined
from .invoice_line import InvoiceLine, InvoiceLineCreate  # noqa: E402
from .payment import Payment  # noqa: E402
from .audit_log import AuditLog  # noqa: E402

Invoice.model_rebuild()
InvoiceCreate.model_rebuild()
