"""
Syriatel API Client

Supports both async and sync operations.
"""

import asyncio
import aiohttp
import re
from datetime import datetime
from typing import Optional, List, Tuple, Union
from .exceptions import raise_error, NetworkError
from .models import Transaction


def _is_phone_number(value: str) -> bool:
    """Check if value is a phone number (10 digits starting with 09)"""
    clean = re.sub(r'\s+', '', str(value))
    # Remove +963 or 963 prefix for checking
    if clean.startswith('+963'):
        clean = '0' + clean[4:]
    elif clean.startswith('963'):
        clean = '0' + clean[3:]
    return len(clean) == 10 and clean.startswith('09') and clean.isdigit()


def _normalize_phone(value: Union[str, int]) -> str:
    """Normalize phone number - remove whitespace and convert +963/963 to 0"""
    s = re.sub(r'\s+', '', str(value))
    if s.startswith('+963'):
        s = '0' + s[4:]
    elif s.startswith('963'):
        s = '0' + s[3:]
    return s


class SyriatelCash:
    """
    Syriatel Cash API namespace
    
    Contains methods for interacting with Syriatel Cash services.
    """
    
    def __init__(self, api: "SyriatelAPI"):
        """Initialize the Cash namespace with API client"""
        self._api = api
    
    async def balance(self, query: Union[str, int, None] = None, number: Union[str, int, None] = None, code: Union[str, int, None] = None) -> float:
        """
        Get Syriatel Cash balance for a phone number or secret code
        
        Args:
            query: Phone number or secret code (auto-detected). If 10 digits starting with 09, treated as phone number.
            number: Phone number (deprecated, use query instead)
            code: Secret code (deprecated, use query instead)
            
        Returns:
            Balance as float (in SYP)
            
        Raises:
            ValueError: If no identifier is provided
            InvalidTokenError: If API token is invalid
            SubscriptionExpiredError: If subscription is expired
            FetchFailedError: If fetch from Syriatel failed
            NotAuthorizedError: If account is not authorized
            ServerMaintenanceError: If servers are under maintenance
            NetworkError: If network request fails
        """
        value = query or number or code
        if not value:
            raise ValueError("A phone number or secret code must be provided")
        
        value_str = str(value)
        params = {}
        
        if _is_phone_number(value_str):
            params["number"] = _normalize_phone(value_str)
        else:
            params["code"] = value_str
        
        data = await self._api._request("GET", "/Balance", params=params)
        return float(data.get("balance", 0))
    
    async def get_incoming_history(
        self,
        query: Union[str, int, None] = None,
        number: Union[str, int, None] = None,
        code: Union[str, int, None] = None,
        page: int = 1,
        status: str = "success",
        start_at: Optional[str] = None,
        end_at: Optional[str] = None,
    ) -> List[Transaction]:
        """
        Get incoming transaction history for Syriatel Cash
        
        Args:
            query: Phone number or secret code (auto-detected). If 10 digits starting with 09, treated as phone number.
            number: Phone number (deprecated, use query instead)
            code: Secret code (deprecated, use query instead)
            page: Page number for pagination (default: 1)
            status: Filter by status - "success" (default), "failed", or "all"
            start_at: Filter transactions from this date (format: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS")
            end_at: Filter transactions until this date (format: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS")
            
        Returns:
            List[Transaction] - List of incoming transactions
            
        Raises:
            ValueError: If no identifier is provided
            InvalidTokenError: If API token is invalid
            SubscriptionExpiredError: If subscription is expired
            FetchFailedError: If fetch from Syriatel failed
            NotAuthorizedError: If account is not authorized
            NetworkError: If network request fails
        """
        value = query or number or code
        if not value:
            raise ValueError("A phone number or secret code must be provided")
        
        value_str = str(value)
        params = {"page": page, "status": status}
        
        if _is_phone_number(value_str):
            params["number"] = _normalize_phone(value_str)
        else:
            params["code"] = value_str
        
        data = await self._api._request("GET", "/IncomingHistory", params=params)
        
        transactions = [
            Transaction.from_dict(tx) for tx in data.get("transactions", [])
        ]
        
        return self._api._filter_transactions_by_date(transactions, start_at, end_at)
    
    async def get_outgoing_history(
        self,
        query: Union[str, int, None] = None,
        number: Union[str, int, None] = None,
        code: Union[str, int, None] = None,
        page: int = 1,
        status: str = "success",
        start_at: Optional[str] = None,
        end_at: Optional[str] = None,
    ) -> List[Transaction]:
        """
        Get outgoing transaction history for Syriatel Cash
        
        Args:
            query: Phone number or secret code (auto-detected). If 10 digits starting with 09, treated as phone number.
            number: Phone number (deprecated, use query instead)
            code: Secret code (deprecated, use query instead)
            page: Page number for pagination (default: 1)
            status: Filter by status - "success" (default), "failed", or "all"
            start_at: Filter transactions from this date (format: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS")
            end_at: Filter transactions until this date (format: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS")
            
        Returns:
            List[Transaction] - List of outgoing transactions
            
        Raises:
            ValueError: If no identifier is provided
            InvalidTokenError: If API token is invalid
            SubscriptionExpiredError: If subscription is expired
            FetchFailedError: If fetch from Syriatel failed
            NotAuthorizedError: If account is not authorized
            NetworkError: If network request fails
        """
        value = query or number or code
        if not value:
            raise ValueError("A phone number or secret code must be provided")
        
        value_str = str(value)
        params = {"page": page, "status": status}
        
        if _is_phone_number(value_str):
            params["number"] = _normalize_phone(value_str)
        else:
            params["code"] = value_str
        
        data = await self._api._request("GET", "/OutgoingHistory", params=params)
        
        transactions = [
            Transaction.from_dict(tx) for tx in data.get("transactions", [])
        ]
        
        return self._api._filter_transactions_by_date(transactions, start_at, end_at)
    
    def find_transaction_by_number(
        self,
        transactions: List[Transaction],
        transaction_no: str,
    ) -> Optional[Transaction]:
        """
        Find a transaction by transaction number
        
        Args:
            transactions: List of Transaction objects to search
            transaction_no: Transaction number to search for
            
        Returns:
            Transaction object if found, None otherwise
        """
        for tx in transactions:
            if tx.transaction_no == transaction_no:
                return tx
        return None
    
    async def find_incoming_transaction(
        self,
        transaction_no: str,
        query: Union[str, int, None] = None,
        number: Union[str, int, None] = None,
        code: Union[str, int, None] = None,
        max_pages: int = 10,
        status: str = "all",
    ) -> Optional[Transaction]:
        """
        Find an incoming transaction by transaction number.
        
        Args:
            transaction_no: Transaction number to find
            query: Phone number or secret code (auto-detected)
            number: Phone number (deprecated, use query instead)
            code: Secret code (deprecated, use query instead)
            max_pages: Maximum pages to search (default: 10)
            status: Filter by status - "success", "failed", or "all" (default)
        
        Returns:
            Transaction: If found.
            None: If searched successfully but not found.
        
        Raises:
            NetworkError, InvalidTokenError, etc.: Propagates errors from get_incoming_history
        """
        value = query or number or code
        if not value:
            raise ValueError("A phone number or secret code must be provided")
        
        for page in range(1, max_pages + 1):
            transactions = await self.get_incoming_history(query=value, page=page, status=status)
            tx = self.find_transaction_by_number(transactions, transaction_no)
            if tx:
                return tx
            if len(transactions) == 0:
                return None
        return None


class SyriatelCashSync:
    """Sync wrapper for SyriatelCash namespace"""
    
    def __init__(self, async_cash: SyriatelCash, run_async_func):
        self._async_cash = async_cash
        self._run_async = run_async_func
    
    def balance(self, query: Union[str, int, None] = None, number: Union[str, int, None] = None, code: Union[str, int, None] = None) -> float:
        """Get balance (sync)"""
        return self._run_async(self._async_cash.balance(query, number, code))
    
    def get_incoming_history(
        self,
        query: Union[str, int, None] = None,
        number: Union[str, int, None] = None,
        code: Union[str, int, None] = None,
        page: int = 1,
        status: str = "success",
        start_at: Optional[str] = None,
        end_at: Optional[str] = None,
    ) -> List[Transaction]:
        """Get incoming history (sync)"""
        return self._run_async(
            self._async_cash.get_incoming_history(query, number, code, page, status, start_at, end_at)
        )
    
    def get_outgoing_history(
        self,
        query: Union[str, int, None] = None,
        number: Union[str, int, None] = None,
        code: Union[str, int, None] = None,
        page: int = 1,
        status: str = "success",
        start_at: Optional[str] = None,
        end_at: Optional[str] = None,
    ) -> List[Transaction]:
        """Get outgoing history (sync)"""
        return self._run_async(
            self._async_cash.get_outgoing_history(query, number, code, page, status, start_at, end_at)
        )
    
    def find_transaction_by_number(
        self,
        transactions: List[Transaction],
        transaction_no: str,
    ) -> Optional[Transaction]:
        """Find transaction by number (sync)"""
        return self._async_cash.find_transaction_by_number(transactions, transaction_no)
    
    def find_incoming_transaction(
        self,
        transaction_no: str,
        query: Union[str, int, None] = None,
        number: Union[str, int, None] = None,
        code: Union[str, int, None] = None,
        max_pages: int = 10,
        status: str = "all",
    ) -> Optional[Transaction]:
        """Find incoming transaction (sync)"""
        return self._run_async(
            self._async_cash.find_incoming_transaction(
                transaction_no, query, number, code, max_pages, status
            )
        )


class SyriatelAPI:
    """
    Async client for Syriatel API
    
    Example:
        ```python
        import asyncio
        from syriatel import SyriatelAPI
        
        async def main():
            async with SyriatelAPI(api_token="your_token") as api:
                # Get numbers
                numbers = await api.get_numbers()
                
                # Use cash namespace - accepts phone number or secret code
                balance = await api.syrcash.balance("0991234567")
                balance = await api.syrcash.balance(6565656)  # Secret code as int
                balance = await api.syrcash.balance("6565656")  # Secret code as string
                
                # Get transaction history (only successful by default)
                transactions = await api.syrcash.get_incoming_history("0991234567")
                
                # Get all transactions including failed
                all_tx = await api.syrcash.get_incoming_history("0991234567", status="all")
                
                # Get only failed transactions
                failed = await api.syrcash.get_incoming_history("0991234567", status="failed")
        
        asyncio.run(main())
        ```
    """
    
    def __init__(
        self,
        api_token: str,
        base_url: str = "https://api.melchersman.com/syr-cash/v1",
        timeout: int = 30,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Initialize the async API client
        
        Args:
            api_token: Your API token
            base_url: Base URL for the API (default: production URL)
            timeout: Request timeout in seconds (default: 30)
            session: Optional aiohttp ClientSession for connection pooling
        """
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session = session
        self._own_session = session is None
        self.syrcash = SyriatelCash(self)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session
    
    async def close(self):
        """Close the client session"""
        if self._session and not self._session.closed and self._own_session:
            await self._session.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _filter_transactions_by_date(
        self,
        transactions: List[Transaction],
        start_at: Optional[str] = None,
        end_at: Optional[str] = None,
    ) -> List[Transaction]:
        """Filter transactions by date range"""
        if not start_at and not end_at:
            return transactions
        
        filtered = []
        for tx in transactions:
            try:
                tx_date = self._parse_date(tx.date)
                
                if start_at:
                    start_dt = self._parse_date(start_at)
                    if tx_date < start_dt:
                        continue
                if end_at:
                    end_dt = self._parse_date(end_at)
                    if tx_date > end_dt:
                        continue
                
                filtered.append(tx)
            except ValueError:
                continue
        
        return filtered
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make an async HTTP request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            
        Returns:
            Response data dictionary
            
        Raises:
            NetworkError: If network request fails
            Various API errors based on response code
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {"api-token": self.api_token}
        
        try:
            session = await self._get_session()
            async with session.request(
                method, url, headers=headers, params=params
            ) as response:
                try:
                    data = await response.json()
                except Exception:
                    raise NetworkError(
                        f"Invalid JSON response: {response.status}",
                        code="NETWORK_ERROR",
                    )
                
                if not data.get("success", False):
                    code = data.get("code", "UNKNOWN_ERROR")
                    raise_error(code, data=data.get("data"))
                
                return data.get("data", {})
        except aiohttp.ClientError as e:
            raise NetworkError(
                f"Network request failed: {str(e)}",
                code="NETWORK_ERROR",
            )
        except Exception as e:
            if isinstance(e, (NetworkError,)):
                raise
            raise NetworkError(
                f"Unexpected error: {str(e)}",
                code="NETWORK_ERROR",
            )
    
    async def get_numbers(self) -> List[str]:
        """
        Get list of all active phone numbers
        
        Returns:
            List[str] - List of phone numbers
            
        Raises:
            InvalidTokenError: If API token is invalid
            NetworkError: If network request fails
        """
        data = await self._request("GET", "/IncomingHistory", params={})
        
        if "numbers" not in data:
            return []
        
        return [item.get("number", "") for item in data["numbers"] if item.get("number")]
    
    async def get_codes(self) -> List[str]:
        """
        Get list of all secret codes for active numbers
        
        Returns:
            List[str] - List of secret codes (may contain empty strings)
            
        Raises:
            InvalidTokenError: If API token is invalid
            NetworkError: If network request fails
        """
        data = await self._request("GET", "/IncomingHistory", params={})
        
        if "numbers" not in data:
            return []
        
        return [item.get("code", "") for item in data["numbers"] if item.get("code")]
    
    async def get_numbers_codes(self) -> List[Tuple[str, str]]:
        """
        Get list of all active numbers with their secret codes
        
        Returns:
            List[Tuple[str, str]] - List of (phone_number, secret_code) tuples
            
        Raises:
            InvalidTokenError: If API token is invalid
            NetworkError: If network request fails
            
        Example:
            ```python
            numbers_codes = await api.get_numbers_codes()
            for number, code in numbers_codes:
                print(f"Number: {number}, Code: {code}")
            ```
        """
        data = await self._request("GET", "/IncomingHistory", params={})
        
        if "numbers" not in data:
            return []
        
        return [
            (item.get("number", ""), item.get("code", ""))
            for item in data["numbers"]
            if item.get("number")
        ]


class SyriatelAPISync:
    """
    Synchronous client for Syriatel API
    
    This is a wrapper around the async client that provides sync methods.
    
    Example:
        ```python
        from syriatel import SyriatelAPISync
        
        api = SyriatelAPISync(api_token="your_token")
        numbers = api.get_numbers()
        balance = api.syrcash.balance("0991234567")
        balance = api.syrcash.balance(6565656)  # Secret code as int works too
        ```
    """
    
    def __init__(
        self,
        api_token: str,
        base_url: str = "https://api.melchersman.com/syr-cash/v1",
        timeout: int = 30,
    ):
        """
        Initialize the sync client
        
        Args:
            api_token: Your API token
            base_url: Base URL for the API (default: production URL)
            timeout: Request timeout in seconds (default: 30)
        """
        self._async_client = SyriatelAPI(
            api_token=api_token,
            base_url=base_url,
            timeout=timeout,
        )
        self.syrcash = SyriatelCashSync(
            self._async_client.syrcash,
            self._run_async
        )
    
    def _run_async(self, coro):
        """Run async coroutine in sync context"""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "Cannot use sync client inside async context. Use SyriatelAPI instead."
            )
        except RuntimeError as e:
            if "Cannot use sync client" in str(e):
                raise
            pass
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def close(self):
        """Close the client"""
        if self._async_client:
            self._run_async(self._async_client.close())
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def get_numbers(self) -> List[str]:
        """Get list of all active phone numbers (sync)"""
        return self._run_async(self._async_client.get_numbers())
    
    def get_codes(self) -> List[str]:
        """Get list of all secret codes (sync)"""
        return self._run_async(self._async_client.get_codes())
    
    def get_numbers_codes(self) -> List[Tuple[str, str]]:
        """Get list of all active numbers with their secret codes (sync)"""
        return self._run_async(self._async_client.get_numbers_codes())
