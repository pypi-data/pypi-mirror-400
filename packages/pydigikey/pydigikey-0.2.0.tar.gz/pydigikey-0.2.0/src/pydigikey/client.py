from typing import TypeVar, Callable, Optional, List, Dict, Any, Union, Type
import asyncio
from math import ceil
import time
import httpx
from pydantic import TypeAdapter, ValidationError
from functools import partial

from .models import (
    Ok, ErrorSignature, ErrorValidation,
    DigikeyCredentials,
    KeywordRequest, KeywordResponse, ProductDetails,
    CategoriesResponse, ManufacturersResponse,
    PricingOptionsForQuantityResponse, DigiReelPricing,
    SortOptions, SortField, SortOrder, QuoteResponse,
    QuotesResponse, AddProductToQuote, AddProductsToQuoteResponse,
    ProductsFromQuoteResponse, OrderResponse, SalesOrder,
    UnexpectedResponse, Result, Ok, Err, AuthTokenResponse,
    DigikeyError
)

Errors = ErrorSignature | ErrorValidation | UnexpectedResponse

class RateLimiter:
    """Handle rate limiting with burst and daily limits"""
    
    def __init__(self):
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 2 requests per second max (120/min)
        
    async def wait_if_needed(self):
        """Wait if needed to respect rate limits"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - elapsed)
        
        self.last_request_time = time.time()

T = TypeVar('T')

class DigiKeyApi:
    def __init__(
        self,
        credentials: DigikeyCredentials,
        sandbox: bool = False,
        locale_site: str = "US",
        locale_language: str = "en",
        locale_currency: str = "USD",
    ):
        self.sandbox = sandbox
        self.host = "sandbox-api.digikey.com" if sandbox else "api.digikey.com"
        self.locale_site = locale_site
        self.locale_language = locale_language
        self.locale_currency = locale_currency
        self.rate_limiter = RateLimiter()
        
        self.creds = credentials
        
        self.client = httpx.AsyncClient(
            base_url=f"https://{self.host}",
            timeout=30.0
        )
    
    async def refresh_auth(self) -> Result[AuthTokenResponse, Any]:
        """Get OAuth2 access token using appropriate grant type"""
        token_url = f"https://{self.host}/v1/oauth2/token"
        data = self.creds.as_auth_req()
        
        async with httpx.AsyncClient() as temp_client:
            response = await temp_client.post(
                token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code >= 300:
                return Err(await self._handle_error(response))
            
            result = DigiKeyApi.validate_response(response, AuthTokenResponse)

            if auth_resp := result.ok():
                self.creds.update_auth(auth_resp)

            return Ok(result)
    
    async def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Get authorization URL for 3-legged OAuth"""
        if not self.creds.redirect_uri:
            raise ValueError("redirect_uri must be set for OAuth")
        
        params = {
            "response_type": "code",
            "client_id": self.creds.client_id,
            "redirect_uri": self.creds.redirect_uri
        }
        
        if state:
            params["state"] = state
        
        auth_url = f"https://{self.host}/v1/oauth2/authorize"
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{auth_url}?{query_string}"

    
    async def exchange_code_for_token(self, code: str) -> Result[AuthTokenResponse, Any]:
        """Exchange authorization code for access token (3-legged OAuth)"""
        if not self.creds.redirect_uri:
            raise ValueError("redirect_uri must be set for 3-legged OAuth")
        
        token_url = f"https://{self.host}/v1/oauth2/token"

        data = {
            **self.creds.as_auth_req(),
            "grant_type": "authorization_code",
            "code": code,
        }
        
        async with httpx.AsyncClient() as temp_client:
            response = await temp_client.post(
                token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            print(data)
            if response.status_code >= 300:
                return Err(await self._handle_error(response))

            result = DigiKeyApi.validate_response(response, AuthTokenResponse)

            if auth_resp := result.ok():
                self.creds.update_auth(auth_resp)

            return result

    def _get_headers(
        self,
        additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Get headers for API request with all required tokens"""
        additional_headers = additional_headers or {}
            
        headers = {
            **self.creds.as_auth_headers(),
            "X-DIGIKEY-Locale-Site": additional_headers.get("site", self.locale_site),
            "X-DIGIKEY-Locale-Language": additional_headers.get("language", self.locale_language),
            "X-DIGIKEY-Locale-Currency": additional_headers.get("currency", self.locale_currency),
            "Content-Type": "application/json",
        }
        
       
        if additional_headers:
            headers.update(additional_headers)

        return headers

    async def _ensure_token_valid(self):
        if time.time() + 30. > (self.creds.access_expiry or 0) and self.creds.refresh_token:
            return await self.refresh_auth()
        elif time.time() > self.creds.refresh_expiry:
            raise RuntimeError("Refresh token expired")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """Make authenticated request to DigiKey API"""
        await self.rate_limiter.wait_if_needed()
        await self._ensure_token_valid()
        
        headers = self._get_headers(headers)
        
        response = await self.client.request(
            method,
            endpoint,
            params=params,
            json=json_data,
            headers=headers
        )
        
        # Check for rate limiting
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                await asyncio.sleep(int(retry_after))
                # Retry once
                return await self._make_request(method, endpoint, params, json_data, headers)
        elif response.status_code >= 300:
            return Err(await self._handle_error(response))
        
        return Ok(response)
    
    @staticmethod
    def _cursor(
        fn: Callable,
        batch_data: List[Any],
        limit: int = 50
    ) -> Result[T, Errors]:
        """Helper for pagination/cursor operations"""
        from .models import Cursorable
        
        collated: Optional[Cursorable] = None
        for i in range(ceil(len(batch_data) / limit)):
            resp = fn(batch_data[limit * i: limit * (i + 1)])
            match resp:
                case Result(Ok=data):
                    if collated is None:
                        collated = data
                    else:
                        collated = collated.extend(data)
                case _:
                    return resp
        
        return Ok(collated)

    @staticmethod
    def validate_response(
        resp: httpx.Response,
        t: Type[T],
    ) -> Result[T, Errors]:
        adapter = TypeAdapter(t)
        try:
            return Ok(adapter.validate_python(resp.json()))
        except ValidationError as e:
            return Err(UnexpectedResponse(message=str(e)))

    @staticmethod
    def validate_respfn(
        t: Type[T]
    ) -> Callable[[Result[Any, Errors]], Result[T, Errors]]:
        return partial(DigiKeyApi.validate_response, t=t)
    
    async def keyword_search(
        self,
        keywords: str,
        limit: int = 20,
        offset: int = 0,
        filter_options: Optional[Dict[str, Any]] = None,
        sort_options: Optional[SortOptions] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[KeywordResponse, Errors]:
        """Search for products by keyword"""
        request_data = KeywordRequest(
            Keywords=keywords,
            Limit=limit,
            Offset=offset,
            FilterOptionsRequest=filter_options,
            SortOptions=sort_options.dict() if sort_options else None
        )
        
        response = await self._make_request(
            "POST",
            "/products/v4/search/keyword",
            json_data=request_data.dict(exclude_none=True),
            headers=headers
        )

        return response.map(DigiKeyApi.validate_respfn(KeywordResponse))
       
    async def product_details(
        self,
        product_number: str,
        manufacturer_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[ProductDetails, Errors]:
        """Get detailed product information"""
        params = {}
        if manufacturer_id:
            params["manufacturerId"] = manufacturer_id
        
        response = await self._make_request(
            "GET",
            f"/products/v4/search/{product_number}/productdetails",
            params=params,
            headers=headers
        )

        return response.map(DigiKeyApi.validate_respfn(ProductDetails))
    
    async def get_manufacturers(
        self,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[ManufacturersResponse, Errors]:
        """Get all manufacturers"""
        response = await self._make_request(
            "GET",
            "/products/v4/search/manufacturers",
            headers=headers
        )

        return response.map(DigiKeyApi.validate_respfn(ManufacturersResponse))
       
    async def get_categories(
        self
    ) -> Result[CategoriesResponse, Errors]:
        """Get all product categories"""
        response = await self._make_request("GET", "/products/v4/search/categories")

        return DigiKeyApi.validate_response(response, CategoriesResponse)
    
    async def get_digireel_pricing(
        self,
        product_number: str,
        requested_quantity: int,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[DigiReelPricing, Errors]:
        """Get Digi-Reel pricing for a product"""
        response = await self._make_request(
            "GET",
            f"/products/v4/search/{product_number}/digireelpricing",
            params={"requestedQuantity": requested_quantity},
            headers=headers
        )

        return response.map(DigiKeyApi.validate_respfn(DigiReelPricing))
    
    async def get_pricing_by_quantity(
        self,
        product_number: str,
        requested_quantity: int,
        manufacturer_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[PricingOptionsForQuantityResponse, Errors]:
        """Get pricing options for specific quantity"""
        params = {}
        if manufacturer_id:
            params["manufacturerId"] = manufacturer_id
        
        response = await self._make_request(
            "GET",
            f"/products/v4/search/{product_number}/pricingbyquantity/{requested_quantity}",
            params=params,
            headers=headers
        )

        return response.map(DigiKeyApi.validate_respfn(PricingOptionsForQuantityResponse))
    
    async def get_recommended_products(
        self,
        product_number: str,
        limit: int = 1,
        search_option_list: Optional[str] = None,
        exclude_market_place_products: bool = False,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[Dict[str, Any], Errors]:
        """Get recommended products"""
        params = {
            "limit": limit,
            "excludeMarketPlaceProducts": exclude_market_place_products
        }
        if search_option_list:
            params["searchOptionList"] = search_option_list
        
        response = await self._make_request(
            "GET",
            f"/products/v4/search/{product_number}/recommendedproducts",
            params=params,
            headers=headers
        )

        return response.map(DigiKeyApi.validate_respfn(Dict[str, Any]))

    async def create_quote(
        self,
        quote_name: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[QuoteResponse, Errors]:
        """Create a new quote"""
        request_data = CreateQuoteRequest(QuoteName=quote_name)
        
        result = await self._make_request(
            "POST",
            "/quoting/v4/quotes",
            json_data=request_data.dict(),
            headers=headers
        )

        return response.map(DigiKeyApi.validate_respfn(QuoteResponse))
    
    async def get_all_quotes(
        self,
        offset: int = 0,
        limit: int = 10
    ) -> Result[QuotesResponse, Errors]:
        """Retrieve all quotes for the account"""
        result = await self._make_request(
            "GET",
            "/quoting/v4/quotes",
            params={"offset": offset, "limit": limit},
        )

        return response.map(DigiKeyApi.validate_respfn(QuotesResponse))
    
    async def get_quote(
        self,
        quote_id: int,
    ) -> Result[QuoteResponse, Errors]:
        """Get a specific quote by ID"""
        result = await self._make_request(
            "GET",
            f"/quoting/v4/quotes/{quote_id}",
        )

        return response.map(DigiKeyApi.validate_respfn(QuoteResponse))
    
    async def add_products_to_quote(
        self,
        quote_id: int,
        products: List[AddProductToQuote],
    ) -> Result[AddProductsToQuoteResponse, Errors]:
        """Add products to a quote"""
        result = await self._make_request(
            "POST",
            f"/quoting/v4/quotes/{quote_id}/details",
            json_data=[p.dict(exclude_none=True) for p in products],
        )

        return response.map(DigiKeyApi.validate_respfn(AddProductsToQuoteResponse))
    
    async def get_products_from_quote(
        self,
        quote_id: int,
        offset: int = 0,
        limit: int = 10
    ) -> Result[ProductsFromQuoteResponse, Errors]:
        """Get products from a specific quote"""
        result = await self._make_request(
            "GET",
            f"/quoting/v4/quotes/{quote_id}/details",
            params={"offset": offset, "limit": limit},
        )

        return response.map(DigiKeyApi.validate_respfn(ProductsFromQuoteResponse))
    
    # OrderStatus API methods
    async def search_orders(
        self,
        shared: bool = False,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 10,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[OrderResponse, Errors]:
        """Search for orders within a date range"""
        params = {
            "Shared": shared,
            "PageNumber": page_number,
            "PageSize": page_size
        }
        
        if start_date:
            params["StartDate"] = start_date
        if end_date:
            params["EndDate"] = end_date
        
        result = await self._make_request(
            "GET",
            "/orderstatus/v4/orders",
            params=params,
            headers=headers
        )

        return response.map(DigiKeyApi.validate_respfn(OrderResponse))
    
    async def retrieve_sales_order(
        self,
        sales_order_id: int,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[SalesOrder, Errors]:
        """Retrieve a specific sales order by ID"""
        result = await self._make_request(
            "GET",
            f"/orderstatus/v4/salesorder/{sales_order_id}",
            headers=headers
        )

        return response.map(DigiKeyApi.validate_respfn(SalesOrder))
    
    async def _handle_error(
        self,
        response: httpx.Response
    ) -> Union[ErrorSignature, ErrorValidation]:
        """Handle API errors"""
        try:
            error_data = response.json()
            
            if response.status_code in [400, 422]:
                return ErrorValidation(
                    statusCode=response.status_code,
                    message=error_data.get("title", "Validation Error"),
                    errors=error_data.get("errors")
                )
            else:
                return ErrorSignature(
                    statusCode=response.status_code,
                    message=error_data.get("title", "API Error"),
                    correlationId=error_data.get("correlationId")
                )
        except:
            return ErrorSignature(
                statusCode=response.status_code,
                message=f"HTTP {response.status_code}",
                correlationId=None
            )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
