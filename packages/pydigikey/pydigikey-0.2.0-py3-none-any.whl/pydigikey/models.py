from typing import TypeVar, Generic, List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, TypeAdapter
from datetime import datetime
from enum import Enum
import time


T = TypeVar('T')
E = TypeVar('E')


class Result(BaseModel, Generic[T, E]):
    """Rust-style Result type for pattern matching"""

    Ok: T | None = None
    Err: E | None = None    
    
    @property
    def is_ok(self) -> bool:
        return self.Err is None
    
    @property
    def is_err(self) -> bool:
        return self.Err is not None
    
    def unwrap(self) -> T:
        """Unwrap the value, raise exception if error"""
        if self.is_err:
            raise ValueError(f"Called unwrap on error: {self.Err}")
        return self.Ok
    
    def unwrap_or(self, default: T) -> T:
        """Unwrap or return default value"""
        return self.Ok if self.is_ok else default
    
    def unwrap_or_else(self, func: callable) -> T:
        """Unwrap or compute value from error"""
        return self.Ok if self.is_ok else func(self.Err)

    def ok(self) -> T | None:
        return self.Ok
    
    def map(self, func: callable) -> 'Result':
        """Map over the value if Ok"""
        if self.is_ok:
            return Ok(func(self.Ok))
        return self
    
    def map_err(self, func: callable) -> 'Result':
        """Map over the error if Err"""
        if self.is_err:
            return Err(func(self.Err))
        return self
    
    def __repr__(self):
        if self.is_ok:
            return f"Ok({self.Ok})"
        return f"Err({self.Err})"
    
    def __eq__(self, other):
        if not isinstance(other, Result):
            return False
        return self.Ok == other.Ok and self.Err == other.Err


def Ok(value: T) -> Result[T, Union['ErrorSignature', 'ErrorValidation']]:
    """Create Ok variant of Result"""
    return Result(Ok=value, Err=None)


def Err(error: Union['ErrorSignature', 'ErrorValidation']) -> Result[None, Union['ErrorSignature', 'ErrorValidation']]:
    """Create Err variant of Result"""
    return Result(Ok=None, Err=error)


class DigikeyError(BaseModel):
    statusCode: int
    message: str
    correlationId: str

class UnexpectedResponse(BaseModel):
    message: str

class ErrorValidation(BaseModel):
    statusCode: int
    message: str
    errors: Optional[Dict[str, List[str]]] = None


class ErrorSignature(BaseModel):
    statusCode: int
    message: str
    correlationId: Optional[str] = None


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: Literal['Bearer']
    expires_in: float
    refresh_token: str
    refresh_token_expires_in: Optional[float] = None


class DigikeyCredentials(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str | None = None
    access_token: str | None = None
    access_expiry: float | None = None
    refresh_token: str | None = None
    refresh_expiry: float | None = None

    def as_auth_headers(self):
        base = {
            "X-DIGIKEY-Client-Id": self.client_id,
        }

        if self.access_token:
            base["Authorization"] = self.access_token

        return base
    
    def update_auth(self, resp: AuthTokenResponse):
        self.access_token = f'Bearer {resp.access_token}'
        self.access_expiry = time.time() + resp.expires_in
        self.refresh_token = resp.refresh_token
        if resp.refresh_token_expires_in:
            self.refresh_expiry = time.time() + resp.refresh_token_expires_in
        else:
            self.refresh_expiry = None
        

    def as_auth_req(self):
        base = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        if self.refresh_token is not None:
            return {
                **base,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "redirect_uri": self.redirect_uri,
            }
        else:
            return {
                **base,
                "grant_type": "client_credentials",
           }


# Cursor interface for pagination
class Cursorable(BaseModel):
    def extend(self, data: Any) -> Any:
        raise NotImplementedError

# Locale models
class IsoSearchLocale(BaseModel):
    Site: str = "US"
    Language: str = "en"
    Currency: str = "USD"


class PriceBreak(BaseModel):
    BreakQuantity: int
    UnitPrice: float
    TotalPrice: float


class Manufacturer(BaseModel):
    Id: int
    Name: str


class PackageType(BaseModel):
    Id: int
    Name: str


class CategoryNode(BaseModel):
    CategoryId: int
    ParentId: Optional[int] = None
    Name: str
    ProductCount: int
    NewProductCount: Optional[int] = None
    ImageUrl: Optional[str] = None
    SeoDescription: Optional[str] = None
    ChildCategories: Optional[List['CategoryNode']] = None


class Description(BaseModel):
    ProductDescription: str
    DetailedDescription: Optional[str] = None


class ProductVariation(BaseModel):
    DigiKeyProductNumber: str
    PackageType: PackageType
    StandardPricing: List[PriceBreak]
    MyPricing: Optional[List[PriceBreak]] = None
    MarketPlace: bool = False
    TariffActive: bool = False
    Supplier: Optional[Dict[str, Any]] = None
    QuantityAvailableforPackageType: int
    MaxQuantityForDistribution: int
    MinimumOrderQuantity: int
    StandardPackage: int
    DigiReelFee: Optional[float] = None


class ProductStatusV4(BaseModel):
    Id: int
    Status: str


class ParameterValue(BaseModel):
    ParameterId: int
    ParameterText: str
    ParameterType: str
    ValueId: str
    ValueText: str


class Classifications(BaseModel):
    ReachStatus: Optional[str] = None
    RohsStatus: Optional[str] = None
    MoistureSensitivityLevel: Optional[str] = None
    ExportControlClassNumber: Optional[str] = None
    HtsusCode: Optional[str] = None


class Product(BaseModel):
    Description: Description
    Manufacturer: Manufacturer
    ManufacturerProductNumber: str
    UnitPrice: float
    DatasheetUrl: Optional[str] = None
    PhotoUrl: Optional[str] = None
    ProductVariations: List[ProductVariation]
    QuantityAvailable: int
    ProductStatus: ProductStatusV4
    BackOrderNotAllowed: Optional[bool] = False
    NormallyStocking: Optional[bool] = False
    Discontinued: Optional[bool] = False
    EndOfLife: Optional[bool] = False
    Ncnr: Optional[bool] = False
    PrimaryVideoUrl: Optional[str] = None
    Parameters: List[ParameterValue]
    BaseProductNumber: Optional[Dict[str, Any]] = None
    Category: CategoryNode
    DateLastBuyChance: Optional[datetime] = None
    ManufacturerLeadWeeks: Optional[str] = None
    ManufacturerPublicQuantity: Optional[int] = None
    Series: Optional[Dict[str, Any]] = None
    ShippingInfo: Optional[str] = None
    Classifications: Optional[Classifications] = None
    OtherNames: Optional[List[str]] = None


class KeywordRequest(BaseModel):
    Keywords: str
    Limit: int = Field(20, ge=1, le=50)
    Offset: int = Field(0, ge=0)
    FilterOptionsRequest: Optional[Dict[str, Any]] = None
    SortOptions: Optional[Dict[str, str]] = None


class KeywordResponse(Cursorable):
    Products: List[Product]
    ProductsCount: int
    ExactMatches: List[Product] = []
    FilterOptions: Optional[Dict[str, Any]] = None
    SearchLocaleUsed: Optional[IsoSearchLocale] = None
    AppliedParametricFiltersDto: List[Dict[str, Any]] = []

    def extend(self, data: 'KeywordResponse') -> 'KeywordResponse':
        """Extend with more data for pagination"""
        self.Products.extend(data.Products)
        self.ExactMatches.extend(data.ExactMatches)
        self.ProductsCount = max(self.ProductsCount, data.ProductsCount)
        return self


class ProductDetails(BaseModel):
    SearchLocaleUsed: IsoSearchLocale
    Product: Product
    AccountIdUsed: Optional[int] = None
    CustomerIdUsed: Optional[int] = None


class CategoriesResponse(Cursorable):
    ProductCount: int
    Categories: List[CategoryNode]
    SearchLocaleUsed: IsoSearchLocale

    def extend(self, data: 'CategoriesResponse') -> 'CategoriesResponse':
        self.Categories.extend(data.Categories)
        self.ProductCount = max(self.ProductCount, data.ProductCount)
        return self


class ManufacturersResponse(Cursorable):
    Manufacturers: List[Manufacturer]

    def extend(self, data: 'ManufacturersResponse') -> 'ManufacturersResponse':
        self.Manufacturers.extend(data.Manufacturers)
        return self


class PricingOptionsForQuantity(BaseModel):
    PricingOption: str
    TotalQuantityPriced: int
    TotalPrice: float
    QuantityAvailable: int
    Products: List[Dict[str, Any]]


class PricingOptionsForQuantityResponse(BaseModel):
    RequestedProduct: str
    RequestedQuantity: int
    ProductUrl: str
    ManufacturerPartNumber: str
    Manufacturer: Manufacturer
    Description: Description
    SettingsUsed: Dict[str, Any]
    MyPricingOptions: List[PricingOptionsForQuantity]
    StandardPricingOptions: List[PricingOptionsForQuantity]
    AccountIdUsed: Optional[int] = None
    CustomerIdUsed: Optional[int] = None


class DigiReelPricing(BaseModel):
    ReelingFee: float
    UnitPrice: float
    ExtendedPrice: float
    RequestedQuantity: int
    SearchLocaleUsed: IsoSearchLocale
    AccountIdUsed: Optional[int] = None
    CustomerIdUsed: Optional[int] = None


class SortField(str, Enum):
    NONE = "None"
    PACKAGING = "Packaging"
    PRODUCT_STATUS = "ProductStatus"
    DIGIKEY_PRODUCT_NUMBER = "DigiKeyProductNumber"
    MANUFACTURER_PRODUCT_NUMBER = "ManufacturerProductNumber"
    MANUFACTURER = "Manufacturer"
    MINIMUM_QUANTITY = "MinimumQuantity"
    QUANTITY_AVAILABLE = "QuantityAvailable"
    PRICE = "Price"
    SUPPLIER = "Supplier"
    PRICE_MANUFACTURER_STANDARD_PACKAGE = "PriceManufacturerStandardPackage"


class SortOrder(str, Enum):
    ASCENDING = "Ascending"
    DESCENDING = "Descending"


class SortOptions(BaseModel):
    Field: SortField = SortField.NONE
    SortOrder: SortOrder = SortOrder.ASCENDING

# digikey_api/models.py (add these models)
class CreateQuoteRequest(BaseModel):
    QuoteName: str = Field(..., max_length=40)


class ExpirationStatus(str, Enum):
    ACTIVE = "Active"
    ERROR = "Error"
    EXPIRED = "Expired"


class ReachStatusCode(str, Enum):
    UNKNOWN = "Unknown"
    AFFECTED = "Affected"
    UNAFFECTED = "Unaffected"
    NOT_APPLICABLE = "NotApplicable"


class RoHSStatusCode(str, Enum):
    UNKNOWN = "Unknown"
    COMPLIANT = "Compliant"
    MIX = "Mix"
    NON_COMPLIANT = "NonCompliant"
    BY_EXCEPTION = "ByException"
    NOT_APPLICABLE = "NotApplicable"
    VENDOR_UNDEFINED = "VendorUndefined"
    COMPLIANT3 = "Compliant3"


class QuoteProductQuantity(BaseModel):
    Quantity: int
    UnitPrice: float
    ExtendedPrice: float


class QuoteProduct(BaseModel):
    DetailId: int
    DigikeyProductNumber: Optional[str] = None
    RequestedProductNumber: str
    ManufacturerProductNumber: Optional[str] = None
    ManufacturerName: Optional[str] = None
    Description: Optional[str] = None
    CustomerReference: Optional[str] = None
    CountryOfOrigin: Optional[str] = None
    PackageType: Optional[str] = None
    MinimumOrderQuantity: Optional[int] = None
    QuantityAvailable: Optional[int] = None
    IsObsolete: bool = False
    IsDiscontinued: bool = False
    IsMfgQuoteRequired: bool = False
    IsMarketplace: bool = False
    RoHSStatus: Optional[RoHSStatusCode] = None
    ReachStatus: Optional[ReachStatusCode] = None
    StandardPackage: Optional[int] = None
    ExpirationDate: Optional[datetime] = None
    IsTariffActive: bool = False
    Quantities: List[QuoteProductQuantity] = []


class QuoteInformation(BaseModel):
    TotalProducts: int
    QuoteId: int
    CustomerId: int
    DateCreated: datetime
    ExpirationStatus: ExpirationStatus
    Currency: str
    QuoteName: str


class QuoteResponse(BaseModel):
    Quote: QuoteInformation


class QuotesResponse(BaseModel):
    TotalQuotes: int
    Quotes: List[QuoteInformation]


class AddProductToQuote(BaseModel):
    ProductNumber: str
    CustomerReference: Optional[str] = Field(None, max_length=40)
    Quantities: List[int]


class AddProductsToQuoteResponse(BaseModel):
    QuoteId: int
    Errors: List[str] = []
    Comments: List[str] = []


class ProductsFromQuoteResponse(BaseModel):
    TotalProducts: int
    QuoteProducts: List[QuoteProduct]


# OrderStatus models
class Contact(BaseModel):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Email: Optional[str] = None


class Address(BaseModel):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    CompanyName: Optional[str] = None
    AddressLine1: Optional[str] = None
    AddressLine2: Optional[str] = None
    AddressLine3: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    County: Optional[str] = None
    ZipCode: Optional[str] = None
    IsoCode: Optional[str] = None
    Phone: Optional[str] = None
    InvoiceId: Optional[int] = None


class ItemShipInfo(BaseModel):
    QuantityShipped: int
    InvoiceId: int
    ShippedDate: datetime
    TrackingNumber: Optional[str] = None
    ExpectedDeliveryDate: Optional[str] = None


class Schedule(BaseModel):
    QuantityScheduled: int
    ScheduledDate: Optional[datetime] = None
    DigiKeyReleaseDate: Optional[datetime] = None


class PackType(str, Enum):
    TAPE_REEL = "TapeReel"
    CUT_TAPE = "CutTape"
    BULK = "Bulk"
    TAPE_BOX = "TapeBox"
    TUBE = "Tube"
    TRAY = "Tray"
    BOX = "Box"
    BAG = "Bag"
    SPOOLS = "Spools"
    DIGI_REEL = "DigiReel"
    STRIP = "Strip"
    BOTTLE = "Bottle"
    CANISTER = "Canister"
    BOOK = "Book"
    DISPENSER = "Dispenser"
    SHEET = "Sheet"
    PAIL = "Pail"
    CAN = "Can"
    CASE = "Case"
    RETAIL_PKG = "RetailPkg"
    DIGI_SPOOL = "DigiSpool"
    ELECTRONIC_DELIVERY = "ElectronicDelivery"
    NONE = "None"


class LineItem(BaseModel):
    SalesOrderId: int
    DetailId: int
    TotalPrice: float
    PurchaseOrder: Optional[str] = None
    CustomerReference: Optional[str] = None
    CountryOfOrigin: Optional[str] = None
    DigiKeyProductNumber: str
    ManufacturerProductNumber: str
    Description: str
    PackType: PackType
    QuantityInitialRequested: int
    QuantityOrdered: int
    QuantityShipped: int
    QuantityReserved: int
    QuantityBackOrder: int
    UnitPrice: float
    PoLineItemNumber: Optional[str] = None
    ItemShipments: List[ItemShipInfo] = []
    Schedules: List[Schedule] = []


class OrderStatusEnum(str, Enum):
    UNKNOWN = "Unknown"
    RECEIVED = "Received"
    PROCESSING = "Processing"
    PROCESSING_PARTIAL_SHIPMENT = "ProcessingPartialShipment"
    PROCESSING_AWAITING_BACKORDERS = "ProcessingAwaitingBackorders"
    PROCESSING_SHIP_BACKORDER = "ProcessingShipBackorder"
    PROCESSING_SCHEDULED_SHIPMENTS_MULTIPLE_RELEASE = "ProcessingScheduledShipmentsMultipleRelease"
    PROCESSING_SCHEDULED_SHIPMENT_SINGLE_RELEASE = "ProcessingScheduledShipmentSingleRelease"
    PROCESSING_SCHEDULED_SHIPMENT_MSC = "ProcessingScheduledShipmentMsc"
    PROCESSING_DK_AND_3RD_PARTY = "ProcessingDkAnd3rdParty"
    PROCESSING_MULTIPLE_3RD_PARTY = "ProcessingMultiple3rdParty"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    GENERIC_DELAY = "GenericDelay"
    CANCELED = "Canceled"
    PROFORMA = "Proforma"
    ACTION_REQUIRED_WIRE_TRANSFER = "ActionRequiredWireTransfer"


class SalesOrderStatusEnum(str, Enum):
    UNKNOWN = "Unknown"
    RECEIVED = "Received"
    PROCESSING = "Processing"
    PROCESSING_3RD_PARTY = "Processing3rdParty"
    PROCESSING_PARTIAL_SHIPMENT = "ProcessingPartialShipment"
    PROCESSING_AWAITING_BACKORDERS = "ProcessingAwaitingBackorders"
    PROCESSING_SHIP_BACKORDER = "ProcessingShipBackorder"
    PROCESSING_SCHEDULED_SHIPMENT_MULTIPLE_RELEASE = "ProcessingScheduledShipmentMultipleRelease"
    PROCESSING_SCHEDULED_SHIPMENT_SINGLE_RELEASE = "ProcessingScheduledShipmentSingleRelease"
    PROCESSING_SCHEDULED_SHIPMENT_MSC = "ProcessingScheduledShipmentMsc"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    GENERIC_DELAY = "GenericDelay"
    CANCELED = "Canceled"
    PROFORMA = "Proforma"
    ACTION_REQUIRED_WIRE_TRANSFER = "ActionRequiredWireTransfer"


class OrderStatusInfo(BaseModel):
    OrderStatus: OrderStatusEnum
    ShortDescription: str
    LongDescription: str


class SalesOrderStatusInfo(BaseModel):
    SalesOrderStatus: SalesOrderStatusEnum
    ShortDescription: str
    LongDescription: str


class SalesOrder(BaseModel):
    CustomerId: int
    Contact: Contact
    SalesOrderId: int
    Status: SalesOrderStatusInfo
    PurchaseOrder: Optional[str] = None
    TotalPrice: float
    DateEntered: datetime
    OrderNumber: int
    ShipMethod: Optional[str] = None
    Currency: str
    ShippingAddress: Address
    LineItems: List[LineItem] = []


class Order(BaseModel):
    OrderNumber: int
    CustomerId: int
    DateEntered: datetime
    Currency: str
    PONumber: Optional[str] = None
    EntireOrderStatus: OrderStatusInfo
    SalesOrders: List[SalesOrder] = []


class OrderResponse(BaseModel):
    TotalOrders: int
    Orders: List[Order]
