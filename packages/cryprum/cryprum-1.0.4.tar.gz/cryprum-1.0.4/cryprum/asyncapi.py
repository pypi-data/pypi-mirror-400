from typing import Any, Dict, Optional

from .base import BaseAsyncClient
from .helpers import AsyncHelperMixin


class AsyncClient(BaseAsyncClient, AsyncHelperMixin):
    async def auth_jwt_v1_post(
        self, access_key: Optional[str] = None, ttl: Optional[int] = None
    ) -> Dict:
        """Generate token"""
        params = None
        json = {"access_key": access_key, "ttl": ttl}
        return await self._request(
            "post", "/v1/auth/jwt".format(**{}), params=params, json=json
        )

    async def tron_account_v1(self, address: str) -> Dict:
        """Getting account information"""
        params = None
        json = None
        return await self._request(
            "get",
            "/v1/tron/account/{address}".format(**{"address": address}),
            params=params,
            json=json,
        )

    async def tron_balances_v1(self, address: str) -> Dict:
        """Getting account balances"""
        params = None
        json = None
        return await self._request(
            "get",
            "/v1/tron/balances/{address}".format(**{"address": address}),
            params=params,
            json=json,
        )

    async def tron_account_v1_post(self) -> Dict:
        """Create an account"""
        params = None
        json = None
        return await self._request(
            "post", "/v1/tron/account".format(**{}), params=params, json=json
        )

    async def tron_transaction_v1(self, txid: str) -> Dict:
        """Getting transaction information"""
        params = None
        json = None
        return await self._request(
            "get",
            "/v1/tron/transaction/{txid}".format(**{"txid": txid}),
            params=params,
            json=json,
        )

    async def tron_transaction_v1_post(
        self,
        amount: Optional[float] = None,
        currency: Optional[str] = None,
        private_key: Optional[str] = None,
        to_address: Optional[str] = None,
    ) -> Dict:
        """Creating a transaction"""
        params = None
        json = {
            "amount": amount,
            "currency": currency,
            "private_key": private_key,
            "to_address": to_address,
        }
        return await self._request(
            "post", "/v1/tron/transaction".format(**{}), params=params, json=json
        )

    async def tron_subscribe_v1_post(
        self, addresses: Optional[Any] = None, currency: Optional[str] = None
    ) -> Dict:
        """Subscribe for notifications (callbacks)"""
        params = None
        json = {"addresses": addresses, "currency": currency}
        return await self._request(
            "post", "/v1/tron/subscribe".format(**{}), params=params, json=json
        )

    async def ethereum_balances_v1(self, address: str) -> Dict:
        """Getting account balances"""
        params = None
        json = None
        return await self._request(
            "get",
            "/v1/ethereum/balances/{address}".format(**{"address": address}),
            params=params,
            json=json,
        )

    async def ethereum_account_v1_post(self) -> Dict:
        """Create an account"""
        params = None
        json = None
        return await self._request(
            "post", "/v1/ethereum/account".format(**{}), params=params, json=json
        )

    async def ethereum_transaction_v1(self, txid: str) -> Dict:
        """Getting transaction information"""
        params = None
        json = None
        return await self._request(
            "get",
            "/v1/ethereum/transaction/{txid}".format(**{"txid": txid}),
            params=params,
            json=json,
        )

    async def ethereum_transaction_v1_post(
        self,
        amount: Optional[float] = None,
        currency: Optional[str] = None,
        private_key: Optional[str] = None,
        to_address: Optional[str] = None,
    ) -> Dict:
        """Creating a transaction"""
        params = None
        json = {
            "amount": amount,
            "currency": currency,
            "private_key": private_key,
            "to_address": to_address,
        }
        return await self._request(
            "post", "/v1/ethereum/transaction".format(**{}), params=params, json=json
        )

    async def ethereum_subscribe_v1_post(
        self, addresses: Optional[Any] = None, currency: Optional[str] = None
    ) -> Dict:
        """Subscribe for notifications (callbacks)"""
        params = None
        json = {"addresses": addresses, "currency": currency}
        return await self._request(
            "post", "/v1/ethereum/subscribe".format(**{}), params=params, json=json
        )

    async def bsc_balances_v1(self, address: str) -> Dict:
        """Getting account balances"""
        params = None
        json = None
        return await self._request(
            "get",
            "/v1/bsc/balances/{address}".format(**{"address": address}),
            params=params,
            json=json,
        )

    async def bsc_account_v1_post(self) -> Dict:
        """Create an account"""
        params = None
        json = None
        return await self._request(
            "post", "/v1/bsc/account".format(**{}), params=params, json=json
        )

    async def bsc_transaction_v1(self, txid: str) -> Dict:
        """Getting transaction information"""
        params = None
        json = None
        return await self._request(
            "get",
            "/v1/bsc/transaction/{txid}".format(**{"txid": txid}),
            params=params,
            json=json,
        )

    async def bsc_transaction_v1_post(
        self,
        amount: Optional[float] = None,
        currency: Optional[str] = None,
        private_key: Optional[str] = None,
        to_address: Optional[str] = None,
    ) -> Dict:
        """Creating a transaction"""
        params = None
        json = {
            "amount": amount,
            "currency": currency,
            "private_key": private_key,
            "to_address": to_address,
        }
        return await self._request(
            "post", "/v1/bsc/transaction".format(**{}), params=params, json=json
        )

    async def bsc_subscribe_v1_post(
        self, addresses: Optional[Any] = None, currency: Optional[str] = None
    ) -> Dict:
        """Subscribe for notifications (callbacks)"""
        params = None
        json = {"addresses": addresses, "currency": currency}
        return await self._request(
            "post", "/v1/bsc/subscribe".format(**{}), params=params, json=json
        )

    async def currencies_rates_v1(self) -> Dict:
        """Rates"""
        params = None
        json = None
        return await self._request(
            "get", "/v1/currencies/rates".format(**{}), params=params, json=json
        )
