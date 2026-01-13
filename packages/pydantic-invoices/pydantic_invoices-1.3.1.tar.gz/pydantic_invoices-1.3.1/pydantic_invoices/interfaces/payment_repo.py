"""Payment repository interface."""

from abc import abstractmethod
from typing import List
from .base import BaseRepository
from ..schemas import Payment, PaymentCreate


class PaymentRepository(BaseRepository[Payment, PaymentCreate]):
    """Abstract payment repository interface."""

    @abstractmethod
    def get_by_invoice(self, invoice_id: int) -> List[Payment]:
        """Get all payments for an invoice."""
        pass

    @abstractmethod
    def get_total_for_invoice(self, invoice_id: int) -> float:
        """Get total amount paid for an invoice."""
        pass
