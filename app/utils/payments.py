"""Payments utils"""
import random
import logging
import payok

from dataclasses import dataclass


@dataclass
class CheckResponse:
    """Check response class"""
    is_paid: bool
    amount: int = 0


@dataclass
class BaseBill:
    """Base bill class"""
    id: int
    url: str = 'https://google.com'


class BasePayment(object):
    """Base payment class"""

    async def check_payment(self, payment_id: int) -> CheckResponse:
        """Check payment"""
        return CheckResponse(True, 1)

    async def create_payment(self, amount: int) -> BaseBill:
        """Create payment"""
        return BaseBill(id=self._get_id())

    @staticmethod
    def _get_id() -> int:
        """Get random id"""
        return random.getrandbits(32)


logger = logging.getLogger('payments')


class PayOK(BasePayment):
    """PayOK class"""

    def __init__(
        self, api_id: int, api_key: str, project_id: int, project_secret: str,
    ) -> None:
        """Initialize the PayOK class"""
        self.api = payok.PayOK(api_id, api_key, project_id, project_secret)

    async def create_payment(self, amount: int) -> BaseBill:
        """Create payment"""
        pay_id = self._get_id()
        url = await self.api.create_bill(
            pay_id=pay_id,
            amount=amount,
        )
        return BaseBill(
            id=pay_id,
            url=url,
        )

    async def check_payment(self, payment_id: int) -> CheckResponse:
        """Check payment"""
        try:
            bills = await self.api.get_transactions(payment_id=payment_id)
        except payok.PayOKError as exc:
            logger.error('PayOk: [%s] %s' % (exc.message, exc.code))
            return CheckResponse(False)

        if not bills:
            return CheckResponse(False)

        bill: payok.Transaction = bills[0]
        return CheckResponse(
            bill.is_paid,
            bill.amount_profit,
        )
