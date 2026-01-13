import asyncio
import threading
import time
from typing import Literal

from .exceptions import CryprumError


Vendor = Literal["ethereum", "tron", "bsc"]


def check(resp):
    if isinstance(resp, (str, bytes)):
        raise CryprumError(resp)
    if detail := resp.get("detail"):
        raise CryprumError(detail)
    return resp


class HelperMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._jwt = {}
        self._last_call = 0
        self._jwt_lock = threading.Lock()

    def __getattribute__(self, key):
        attr = super().__getattribute__(key)
        if not callable(attr) or key.startswith("_"):
            return attr
        with self._jwt_lock:
            if (time.time() - self._last_call) > 3333:
                self._last_call = int(time.time())
                auth = super().__getattribute__("auth_jwt_v1_post")
                self._jwt = auth(self._token, ttl=3600)
                check(self._jwt)
            self._headers.update(
                {"Authorization": "Bearer {token}".format(**self._jwt)}
            )
        return attr

    def balances(self, vendor: Vendor, address):
        resp = getattr(self, f"{vendor}_balances_v1")(address)
        return check(resp)

    def transaction_info(self, vendor: Vendor, txid: str):
        resp = getattr(self, f"{vendor}_transaction_v1")(txid)
        return check(resp)

    def transaction(
        self,
        vendor: Vendor,
        amount: int,
        currency: str,
        private_key: str,
        to_address: str,
    ):
        resp = getattr(self, f"{vendor}_transaction_v1_post")(
            amount=amount,
            currency=currency,
            private_key=private_key,
            to_address=to_address,
        )
        return check(resp)

    def subscribe(self, vendor: Vendor, addresses: list):
        return check(getattr(self, f"{vendor}_subscribe_v1_post")(addresses))

    def operation_status(self, operation_id: str):
        resp = self.operation_v1(operation_id)
        return check(resp)


class AsyncHelperMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._jwt = {}
        self._last_call = 0
        self._jwt_lock = asyncio.Lock()

    async def _auth(self, *a, **kw):
        async with self._jwt_lock:
            if (time.time() - self._last_call) > 3333:
                self._last_call = int(time.time())
                auth = super().__getattribute__("auth_jwt_v1_post")
                self._jwt = await auth(self._token, ttl=3600)
                check(self._jwt)
            self._headers.update(
                {"Authorization": "Bearer {token}".format(**self._jwt)}
            )
        return await self._method(*a, **kw)

    def __getattribute__(self, key):
        method = super().__getattribute__(key)
        if not key.startswith("_"):
            self._method = method
            return self._auth
        return method

    async def balances(self, vendor: Vendor, address):
        return await getattr(self, f"{vendor}_balances_v1")(address)

    async def transaction_info(self, vendor: Vendor, txid: str):
        return await getattr(self, f"{vendor}_transaction_v1")(txid)

    async def transaction(
        self,
        vendor: Vendor,
        amount: int,
        currency: str,
        private_key: str,
        to_address: str,
    ):
        return await getattr(self, f"{vendor}_transaction_v1_post")(
            amount=amount,
            currency=currency,
            private_key=private_key,
            to_address=to_address,
        )

    async def subscribe(self, vendor: Vendor, addresses: list):
        return await getattr(self, f"{vendor}_subscribe_v1_post")(addresses)

    async def operation_status(self, operation_id: str):
        resp = await self.operation_v1(operation_id)
        return check(resp)
