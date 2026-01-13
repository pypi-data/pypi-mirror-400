"""
Data models for Alura SDK
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum


# =============================================================================
# Enums (Paid AI Compatible)
# =============================================================================

class ChargeType(str, Enum):
    """Type of charge for pricing."""
    ONE_TIME = "oneTime"
    RECURRING = "recurring"
    USAGE = "usage"
    SEAT_BASED = "seatBased"


class PricingModelType(str, Enum):
    """Pricing model type."""
    PER_UNIT = "PerUnit"
    VOLUME_PRICING = "VolumePricing"
    GRADUATED_PRICING = "GraduatedPricing"


class BillingFrequency(str, Enum):
    """Billing frequency for recurring charges."""
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    SEMI_ANNUAL = "SemiAnnual"
    ANNUAL = "Annual"


class CreationState(str, Enum):
    """Order/order line creation state."""
    DRAFT = "draft"
    ACTIVE = "active"


class Currency(str, Enum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


@dataclass
class Action:
    """Represents a trackable action/event from an AI agent"""
    event_name: str
    agent_id: str
    customer_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    external_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to API payload"""
        payload = {
            "agent_code": self.agent_id,
            "event_name": self.event_name,
            "data": self.data,
        }
        if self.external_id:
            payload["external_id"] = self.external_id
        if self.timestamp:
            payload["timestamp"] = self.timestamp.isoformat()
        if self.customer_id:
            payload["data"]["customer_id"] = self.customer_id
        return payload


# Backward compatibility alias
Signal = Action


@dataclass
class Address:
    """Billing/shipping address"""
    line_1: str = ""
    line_2: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = ""

    def to_dict(self) -> dict:
        return {
            "addressLine1": self.line_1,
            "addressLine2": self.line_2,
            "city": self.city,
            "state": self.state,
            "postalCode": self.zip_code,
            "country": self.country,
        }


# =============================================================================
# Customer Enums (Paid AI Compatible)
# =============================================================================

class TaxExemptStatus(str, Enum):
    """Tax exempt status for customers."""
    NONE = "none"
    EXEMPT = "exempt"
    REVERSE = "reverse"


class CreationSource(str, Enum):
    """Source of customer creation."""
    MANUAL = "manual"
    API = "api"
    CRM = "crm"
    OTHER = "other"


@dataclass
class Customer:
    """
    Represents a customer/account in Alura.

    Maps to Paid.ai's Account concept.
    """
    id: Optional[str] = None
    organization_id: Optional[str] = None
    name: str = ""
    phone: str = ""
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    tax_exempt_status: str = "none"
    creation_source: str = "api"
    website: str = ""
    external_id: str = ""
    creation_state: str = "active"
    billing_address: Optional[Address] = None
    # Legacy/additional fields
    email: str = ""
    company_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Customer":
        """Create Customer from API response"""
        # Parse billing address if present
        billing_address = None
        if data.get("billingAddress") or data.get("billing_address"):
            addr_data = data.get("billingAddress") or data.get("billing_address")
            if addr_data:
                billing_address = Address(
                    line_1=addr_data.get("line1", addr_data.get("line_1", "")),
                    line_2=addr_data.get("line2", addr_data.get("line_2", "")),
                    city=addr_data.get("city", ""),
                    state=addr_data.get("state", ""),
                    zip_code=addr_data.get("zipCode", addr_data.get("zip_code", "")),
                    country=addr_data.get("country", ""),
                )

        return cls(
            id=str(data.get("id")) if data.get("id") else None,
            organization_id=data.get("organizationId", data.get("organization_id")),
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            employee_count=data.get("employeeCount", data.get("employee_count")),
            annual_revenue=data.get("annualRevenue", data.get("annual_revenue")),
            tax_exempt_status=data.get("taxExemptStatus", data.get("tax_exempt_status", "none")),
            creation_source=data.get("creationSource", data.get("creation_source", "api")),
            website=data.get("website", ""),
            external_id=data.get("externalId", data.get("external_id", "")),
            creation_state=data.get("creationState", data.get("creation_state", "active")),
            billing_address=billing_address,
            email=data.get("email", ""),
            company_name=data.get("companyName", data.get("company_name", "")),
            metadata=data.get("metadata", {}),
            is_active=data.get("isActive", data.get("is_active", True)),
            created_at=datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00")) if data.get("createdAt") else None,
            updated_at=datetime.fromisoformat(data["updatedAt"].replace("Z", "+00:00")) if data.get("updatedAt") else None,
        )

    def to_dict(self) -> dict:
        """Convert to API payload for create/update."""
        result = {
            "name": self.name,
        }
        if self.phone:
            result["phone"] = self.phone
        if self.employee_count is not None:
            result["employeeCount"] = self.employee_count
        if self.annual_revenue is not None:
            result["annualRevenue"] = self.annual_revenue
        if self.tax_exempt_status:
            result["taxExemptStatus"] = self.tax_exempt_status
        if self.creation_source:
            result["creationSource"] = self.creation_source
        if self.website:
            result["website"] = self.website
        if self.external_id:
            result["externalId"] = self.external_id
        if self.billing_address:
            result["billingAddress"] = self.billing_address.to_dict()
        if self.email:
            result["email"] = self.email
        if self.company_name:
            result["companyName"] = self.company_name
        if self.metadata:
            result["metadata"] = self.metadata
        return result


@dataclass
class Contact:
    """
    Represents a contact person for a customer.
    """
    id: Optional[int] = None
    customer_id: Optional[int] = None
    salutation: str = ""
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    external_id: str = ""
    billing_street: str = ""
    billing_city: str = ""
    billing_state_province: str = ""
    billing_country: str = ""
    billing_postal_code: str = ""
    is_primary: bool = False
    receives_invoices: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Contact":
        """Create Contact from API response"""
        return cls(
            id=data.get("id"),
            customer_id=data.get("accountId"),
            salutation=data.get("salutation", ""),
            first_name=data.get("firstName", ""),
            last_name=data.get("lastName", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            external_id=data.get("externalId", ""),
            billing_street=data.get("billingAddressLine1", ""),
            billing_city=data.get("billingCity", ""),
            billing_state_province=data.get("billingState", ""),
            billing_country=data.get("billingCountry", ""),
            billing_postal_code=data.get("billingPostalCode", ""),
            is_primary=data.get("isPrimary", False),
            receives_invoices=data.get("receivesInvoices", True),
            metadata=data.get("metadata", {}),
            is_active=data.get("isActive", True),
            created_at=datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00")) if data.get("createdAt") else None,
            updated_at=datetime.fromisoformat(data["updatedAt"].replace("Z", "+00:00")) if data.get("updatedAt") else None,
        )

    @property
    def full_name(self) -> str:
        parts = [self.salutation, self.first_name, self.last_name]
        return " ".join(p for p in parts if p)


# =============================================================================
# Order Line and Pricing Models (Paid AI Compatible)
# =============================================================================

@dataclass
class Tier:
    """Pricing tier for volume/graduated pricing."""
    lower_bound: int = 0
    upper_bound: Optional[int] = None
    price: float = 0.0

    @classmethod
    def from_dict(cls, data: dict) -> "Tier":
        return cls(
            lower_bound=data.get("lowerBound", data.get("min_quantity", 0)),
            upper_bound=data.get("upperBound", data.get("max_quantity")),
            price=data.get("price", data.get("unit_price", 0.0)),
        )

    def to_dict(self) -> dict:
        result = {
            "lowerBound": self.lower_bound,
            "price": self.price,
        }
        if self.upper_bound is not None:
            result["upperBound"] = self.upper_bound
        return result


@dataclass
class PricePoint:
    """Price point configuration for an attribute."""
    currency: str = "USD"
    unit_price: float = 0.0
    tiers: List[Tier] = field(default_factory=list)
    min_quantity: int = 0
    included_quantity: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "PricePoint":
        tiers = []
        if data.get("tiers"):
            tiers = [Tier.from_dict(t) for t in data["tiers"]]
        return cls(
            currency=data.get("currency", "USD"),
            unit_price=data.get("unit_price", data.get("unitPrice", 0.0)),
            tiers=tiers,
            min_quantity=data.get("min_quantity", data.get("minQuantity", 0)),
            included_quantity=data.get("included_quantity", data.get("includedQuantity", 0)),
        )

    def to_dict(self) -> dict:
        return {
            "currency": self.currency,
            "unitPrice": self.unit_price,
            "tiers": [t.to_dict() for t in self.tiers],
            "minQuantity": self.min_quantity,
            "includedQuantity": self.included_quantity,
        }


@dataclass
class OrderLineAttributePricing:
    """Pricing configuration for an order line attribute."""
    event_name: str = ""
    charge_type: str = "recurring"
    price_point: Optional[PricePoint] = None
    price_points: Dict[str, PricePoint] = field(default_factory=dict)
    pricing_model: str = "PerUnit"
    billing_frequency: str = "Monthly"
    taxable: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "OrderLineAttributePricing":
        price_point = None
        price_points = {}

        # Handle both single price_point and multi-currency price_points
        if data.get("price_point") or data.get("pricePoint"):
            pp_data = data.get("price_point") or data.get("pricePoint")
            price_point = PricePoint.from_dict(pp_data)

        if data.get("price_points") or data.get("pricePoints"):
            pp_dict = data.get("price_points") or data.get("pricePoints")
            for currency, pp_data in pp_dict.items():
                price_points[currency] = PricePoint.from_dict(pp_data)

        return cls(
            event_name=data.get("event_name", data.get("eventName", "")),
            charge_type=data.get("charge_type", data.get("chargeType", "recurring")),
            price_point=price_point,
            price_points=price_points,
            pricing_model=data.get("pricing_model", data.get("pricingModel", "PerUnit")),
            billing_frequency=data.get("billing_frequency", data.get("billingFrequency", "Monthly")),
            taxable=data.get("taxable", True),
        )

    def to_dict(self) -> dict:
        result = {
            "eventName": self.event_name,
            "chargeType": self.charge_type,
            "pricingModel": self.pricing_model,
            "billingFrequency": self.billing_frequency,
            "taxable": self.taxable,
        }
        if self.price_point:
            result["pricePoint"] = self.price_point.to_dict()
        if self.price_points:
            result["pricePoints"] = {k: v.to_dict() for k, v in self.price_points.items()}
        return result


@dataclass
class OrderLineAttribute:
    """Attribute configuration for an order line."""
    id: Optional[str] = None
    agent_attribute_id: Optional[str] = None
    order_line_id: Optional[str] = None
    quantity: int = 0
    currency: str = "USD"
    pricing: Optional[OrderLineAttributePricing] = None
    status: str = ""
    total_amount: float = 0.0
    last_billing_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    billing_cycle_start: Optional[datetime] = None
    billing_cycle_end: Optional[datetime] = None
    creation_state: str = "active"
    agent_attributes: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: dict) -> "OrderLineAttribute":
        pricing = None
        if data.get("pricing"):
            pricing = OrderLineAttributePricing.from_dict(data["pricing"])

        return cls(
            id=data.get("id"),
            agent_attribute_id=data.get("agent_attribute_id", data.get("agentAttributeId")),
            order_line_id=data.get("order_line_id", data.get("orderLineId")),
            quantity=data.get("quantity", 0),
            currency=data.get("currency", "USD"),
            pricing=pricing,
            status=data.get("status", ""),
            total_amount=data.get("total_amount", data.get("totalAmount", 0.0)),
            creation_state=data.get("creation_state", data.get("creationState", "active")),
            agent_attributes=data.get("agent_attributes", data.get("agentAttributes")),
        )

    def to_dict(self) -> dict:
        result = {
            "agentAttributeId": self.agent_attribute_id,
            "quantity": self.quantity,
            "currency": self.currency,
        }
        if self.pricing:
            result["pricing"] = self.pricing.to_dict()
        return result


@dataclass
class OrderLine:
    """
    Represents an order line linking an order to an agent.

    Paid AI compatible order line structure.
    """
    id: Optional[str] = None
    order_id: Optional[str] = None
    agent_id: Optional[str] = None
    agent_external_id: Optional[str] = None
    name: str = ""
    description: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_amount: float = 0.0
    billed_amount_without_tax: float = 0.0
    billed_tax: float = 0.0
    total_billed_amount: float = 0.0
    agent: Optional[Dict[str, Any]] = None
    order_line_attributes: List[OrderLineAttribute] = field(default_factory=list)
    creation_state: str = "active"

    @classmethod
    def from_dict(cls, data: dict) -> "OrderLine":
        order_line_attributes = []
        if data.get("order_line_attributes") or data.get("orderLineAttributes"):
            attrs = data.get("order_line_attributes") or data.get("orderLineAttributes") or []
            order_line_attributes = [OrderLineAttribute.from_dict(a) for a in attrs]

        start_date = None
        if data.get("start_date") or data.get("startDate"):
            date_str = data.get("start_date") or data.get("startDate")
            if date_str:
                start_date = date.fromisoformat(date_str[:10]) if isinstance(date_str, str) else date_str

        end_date = None
        if data.get("end_date") or data.get("endDate"):
            date_str = data.get("end_date") or data.get("endDate")
            if date_str:
                end_date = date.fromisoformat(date_str[:10]) if isinstance(date_str, str) else date_str

        return cls(
            id=data.get("id"),
            order_id=data.get("order_id", data.get("orderId")),
            agent_id=data.get("agent_id", data.get("agentId")),
            agent_external_id=data.get("agent_external_id", data.get("agentExternalId")),
            name=data.get("name", ""),
            description=data.get("description", ""),
            start_date=start_date,
            end_date=end_date,
            total_amount=data.get("total_amount", data.get("totalAmount", 0.0)),
            billed_amount_without_tax=data.get("billed_amount_without_tax", data.get("billedAmountWithoutTax", 0.0)),
            billed_tax=data.get("billed_tax", data.get("billedTax", 0.0)),
            total_billed_amount=data.get("total_billed_amount", data.get("totalBilledAmount", 0.0)),
            agent=data.get("agent"),
            order_line_attributes=order_line_attributes,
            creation_state=data.get("creation_state", data.get("creationState", "active")),
        )

    def to_dict(self) -> dict:
        result = {}
        if self.agent_id:
            result["agentId"] = self.agent_id
        if self.agent_external_id:
            result["agentExternalId"] = self.agent_external_id
        if self.name:
            result["name"] = self.name
        if self.description:
            result["description"] = self.description
        if self.start_date:
            result["startDate"] = self.start_date.isoformat()
        if self.end_date:
            result["endDate"] = self.end_date.isoformat()
        if self.order_line_attributes:
            result["orderLineAttributes"] = [a.to_dict() for a in self.order_line_attributes]
        return result


@dataclass
class Order:
    """
    Represents an order/subscription linking a customer to an agent.

    Paid AI compatible order structure with order_lines support.
    """
    id: Optional[str] = None
    name: str = ""
    description: str = ""
    order_number: str = ""
    external_id: str = ""
    account_id: Optional[str] = None
    organization_id: Optional[str] = None
    customer_id: Optional[int] = None  # Alias for account_id (Alura style)
    agent_id: Optional[int] = None
    agent_code: str = ""
    billing_contact_id: Optional[int] = None
    status: str = "pending"
    creation_state: str = "draft"
    billing_frequency: str = "monthly"
    seat_count: int = 1
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    # Paid AI compatible amount fields
    total_amount: float = 0.0
    order_amount: float = 0.0
    estimated_tax: float = 0.0
    billed_amount_no_tax: float = 0.0
    billed_tax: float = 0.0
    total_billed_amount: float = 0.0
    pending_billing_amount: float = 0.0
    # Order lines (Paid AI style)
    order_lines: List[OrderLine] = field(default_factory=list)
    # Account info (Paid AI style)
    account: Optional[Dict[str, Any]] = None
    # Legacy Alura fields
    pricing_snapshot: List[dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    usage_summary: List[dict] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """Create Order from API response"""
        # Parse order lines
        order_lines = []
        if data.get("order_lines") or data.get("orderLines"):
            lines_data = data.get("order_lines") or data.get("orderLines") or []
            order_lines = [OrderLine.from_dict(line) for line in lines_data]

        # Parse start_date - handle both date string and datetime string
        start_date = None
        if data.get("startDate") or data.get("start_date"):
            date_str = data.get("startDate") or data.get("start_date")
            if date_str:
                start_date = date.fromisoformat(date_str[:10]) if isinstance(date_str, str) else date_str

        # Parse end_date
        end_date = None
        if data.get("endDate") or data.get("end_date"):
            date_str = data.get("endDate") or data.get("end_date")
            if date_str:
                end_date = date.fromisoformat(date_str[:10]) if isinstance(date_str, str) else date_str

        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            order_number=data.get("orderNumber", ""),
            external_id=data.get("externalId", ""),
            account_id=data.get("accountId") or data.get("account_id"),
            organization_id=data.get("organizationId") or data.get("organization_id"),
            customer_id=data.get("accountId") or data.get("customerId"),
            agent_id=data.get("agentId"),
            agent_code=data.get("agentCode", ""),
            billing_contact_id=data.get("billingContactId"),
            status=data.get("status", "pending"),
            creation_state=data.get("creationState", data.get("creation_state", "draft")),
            billing_frequency=data.get("billingFrequency", "monthly"),
            seat_count=data.get("seatCount", 1),
            start_date=start_date,
            end_date=end_date,
            total_amount=data.get("totalAmount", data.get("total_amount", 0.0)),
            order_amount=data.get("orderAmount", data.get("order_amount", 0.0)),
            estimated_tax=data.get("estimatedTax", data.get("estimated_tax", 0.0)),
            billed_amount_no_tax=data.get("billedAmountNoTax", data.get("billed_amount_no_tax", 0.0)),
            billed_tax=data.get("billedTax", data.get("billed_tax", 0.0)),
            total_billed_amount=data.get("totalBilledAmount", data.get("total_billed_amount", 0.0)),
            pending_billing_amount=data.get("pendingBillingAmount", data.get("pending_billing_amount", 0.0)),
            order_lines=order_lines,
            account=data.get("account"),
            pricing_snapshot=data.get("pricingSnapshot", []),
            metadata=data.get("metadata", {}),
            usage_summary=data.get("usageSummary", data.get("usage_summary", [])),
            created_at=datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00")) if data.get("createdAt") else None,
            updated_at=datetime.fromisoformat(data["updatedAt"].replace("Z", "+00:00")) if data.get("updatedAt") else None,
        )


# =============================================================================
# Entitlement/Credit Bundle Models (Paid AI Compatible)
# =============================================================================

@dataclass
class EntitlementUsage:
    """
    Represents entitlement/credit bundle usage for a customer.

    Maps to Paid AI's credit-bundles endpoint response.
    """
    id: Optional[str] = None
    organization_id: Optional[str] = None
    product_id: Optional[str] = None
    entitlement_id: Optional[str] = None
    customer_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total: int = 0
    available: int = 0
    used: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "EntitlementUsage":
        """Create EntitlementUsage from API response"""
        def parse_dt(value):
            if not value:
                return None
            if isinstance(value, datetime):
                return value
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        return cls(
            id=str(data.get("id")) if data.get("id") else None,
            organization_id=data.get("organizationId", data.get("organization_id")),
            product_id=data.get("productId", data.get("product_id")),
            entitlement_id=data.get("entitlementId", data.get("entitlement_id")),
            customer_id=data.get("customerId", data.get("customer_id")),
            start_date=parse_dt(data.get("startDate", data.get("start_date"))),
            end_date=parse_dt(data.get("endDate", data.get("end_date"))),
            total=data.get("total", 0),
            available=data.get("available", 0),
            used=data.get("used", 0),
            created_at=parse_dt(data.get("createdAt", data.get("created_at"))),
            updated_at=parse_dt(data.get("updatedAt", data.get("updated_at"))),
        )


# =============================================================================
# Cost Trace Models (Paid AI Compatible)
# =============================================================================

@dataclass
class CostAmount:
    """Cost amount with currency."""
    amount: float = 0.0
    currency: str = "USD"

    @classmethod
    def from_dict(cls, data: dict) -> "CostAmount":
        return cls(
            amount=data.get("amount", 0.0),
            currency=data.get("currency", "USD"),
        )


@dataclass
class CostTrace:
    """
    Represents a cost trace for an LLM operation.

    Maps to Paid AI's costs endpoint response.
    """
    name: str = ""
    vendor: str = ""
    model: str = ""
    cost: Optional[CostAmount] = None
    start_time_unix_nano: str = ""
    end_time_unix_nano: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "CostTrace":
        """Create CostTrace from API response"""
        cost = None
        if data.get("cost"):
            cost = CostAmount.from_dict(data["cost"])

        return cls(
            name=data.get("name", ""),
            vendor=data.get("vendor", ""),
            model=data.get("model", ""),
            cost=cost,
            start_time_unix_nano=data.get("startTimeUnixNano", ""),
            end_time_unix_nano=data.get("endTimeUnixNano", ""),
            attributes=data.get("attributes", {}),
        )

    @property
    def total_cost(self) -> float:
        """Get the total cost amount."""
        return self.cost.amount if self.cost else 0.0


@dataclass
class CostTracesResponse:
    """Response from costs endpoint with pagination."""
    traces: List[CostTrace] = field(default_factory=list)
    limit: int = 100
    offset: int = 0
    count: int = 0
    has_more: bool = False
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    external_customer_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "CostTracesResponse":
        """Create CostTracesResponse from API response"""
        traces = []
        if data.get("traces"):
            traces = [CostTrace.from_dict(t) for t in data["traces"]]

        meta = data.get("meta", {})
        return cls(
            traces=traces,
            limit=meta.get("limit", 100),
            offset=meta.get("offset", 0),
            count=meta.get("count", len(traces)),
            has_more=meta.get("hasMore", False),
            start_time=meta.get("startTime"),
            end_time=meta.get("endTime"),
            external_customer_id=meta.get("externalCustomerId"),
        )


# =============================================================================
# Usage Summary Models (Paid AI Compatible)
# =============================================================================

@dataclass
class UsageSummaryOrder:
    """Order reference in usage summary."""
    id: str = ""
    display_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "UsageSummaryOrder":
        if not data:
            return None
        return cls(
            id=str(data.get("id", "")),
            display_id=data.get("displayId"),
        )


@dataclass
class UsageSummaryOrderLine:
    """Order line reference in usage summary."""
    id: str = ""
    display_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "UsageSummaryOrderLine":
        if not data:
            return None
        return cls(
            id=str(data.get("id", "")),
            display_id=data.get("displayId"),
        )


@dataclass
class UsageSummary:
    """
    Represents aggregated usage for a billing period.

    Maps to Paid AI's usage endpoint response.
    """
    id: Optional[str] = None
    event_name: str = ""
    events_quantity: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    subtotal: int = 0
    next_billing_date: Optional[datetime] = None
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    order_line_id: Optional[str] = None
    order_line_attribute_id: Optional[str] = None
    invoice_id: Optional[str] = None
    invoice_line_id: Optional[str] = None
    order: Optional[UsageSummaryOrder] = None
    order_line: Optional[UsageSummaryOrderLine] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "UsageSummary":
        """Create UsageSummary from API response"""
        def parse_dt(value):
            if not value:
                return None
            if isinstance(value, datetime):
                return value
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        order = None
        if data.get("order"):
            order = UsageSummaryOrder.from_dict(data["order"])

        order_line = None
        if data.get("orderLine"):
            order_line = UsageSummaryOrderLine.from_dict(data["orderLine"])

        return cls(
            id=str(data.get("id")) if data.get("id") else None,
            event_name=data.get("eventName", data.get("event_name", "")),
            events_quantity=data.get("eventsQuantity", data.get("events_quantity", 0)),
            start_date=parse_dt(data.get("startDate", data.get("start_date"))),
            end_date=parse_dt(data.get("endDate", data.get("end_date"))),
            subtotal=data.get("subtotal", 0),
            next_billing_date=parse_dt(data.get("nextBillingDate", data.get("next_billing_date"))),
            customer_id=data.get("customerId", data.get("customer_id")),
            order_id=data.get("orderId", data.get("order_id")),
            order_line_id=data.get("orderLineId", data.get("order_line_id")),
            order_line_attribute_id=data.get("orderLineAttributeId", data.get("order_line_attribute_id")),
            invoice_id=data.get("invoiceId", data.get("invoice_id")),
            invoice_line_id=data.get("invoiceLineId", data.get("invoice_line_id")),
            order=order,
            order_line=order_line,
            created_at=parse_dt(data.get("createdAt", data.get("created_at"))),
            updated_at=parse_dt(data.get("updatedAt", data.get("updated_at"))),
        )


@dataclass
class UsageSummariesResponse:
    """Response from usage endpoint with pagination."""
    data: List[UsageSummary] = field(default_factory=list)
    limit: int = 100
    offset: int = 0
    total: int = 0
    has_more: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "UsageSummariesResponse":
        """Create UsageSummariesResponse from API response"""
        summaries = []
        if data.get("data"):
            summaries = [UsageSummary.from_dict(s) for s in data["data"]]

        pagination = data.get("pagination", {})
        return cls(
            data=summaries,
            limit=pagination.get("limit", 100),
            offset=pagination.get("offset", 0),
            total=pagination.get("total", len(summaries)),
            has_more=pagination.get("hasMore", False),
        )


# =============================================================================
# Product Models (Paid AI Compatible)
# =============================================================================

class ProductType(str, Enum):
    """Type of product."""
    AGENT = "agent"
    PRODUCT = "product"
    PREPAID_CREDIT_BUNDLE = "prepaidCreditBundle"


@dataclass
class AgentPricePointTiers:
    """Pricing tier for volume/graduated pricing."""
    min_quantity: float = 0.0
    max_quantity: Optional[float] = None
    unit_price: float = 0.0

    @classmethod
    def from_dict(cls, data: dict) -> "AgentPricePointTiers":
        return cls(
            min_quantity=data.get("minQuantity", data.get("min_quantity", 0.0)),
            max_quantity=data.get("maxQuantity", data.get("max_quantity")),
            unit_price=data.get("unitPrice", data.get("unit_price", 0.0)),
        )

    def to_dict(self) -> dict:
        result = {
            "minQuantity": self.min_quantity,
            "unitPrice": self.unit_price,
        }
        if self.max_quantity is not None:
            result["maxQuantity"] = self.max_quantity
        return result


@dataclass
class AgentPricePoint:
    """Price point configuration."""
    unit_price: float = 0.0
    min_quantity: float = 0.0
    included_quantity: float = 0.0
    tiers: List[AgentPricePointTiers] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "AgentPricePoint":
        tiers = []
        if data.get("tiers"):
            tiers = [AgentPricePointTiers.from_dict(t) for t in data["tiers"]]
        return cls(
            unit_price=data.get("unitPrice", data.get("unit_price", 0.0)),
            min_quantity=data.get("minQuantity", data.get("min_quantity", 0.0)),
            included_quantity=data.get("includedQuantity", data.get("included_quantity", 0.0)),
            tiers=tiers,
        )

    def to_dict(self) -> dict:
        result = {
            "unitPrice": self.unit_price,
            "minQuantity": self.min_quantity,
            "includedQuantity": self.included_quantity,
        }
        if self.tiers:
            result["tiers"] = [t.to_dict() for t in self.tiers]
        return result


@dataclass
class ProductPricing:
    """Pricing configuration for a product attribute."""
    event_name: str = ""
    taxable: bool = True
    credit_cost: Optional[float] = None
    charge_type: str = "usage"  # oneTime, recurring, usage, seatBased
    pricing_model: str = "PerUnit"  # PerUnit, VolumePricing, GraduatedPricing, PrepaidCredits
    billing_frequency: str = "monthly"  # monthly, quarterly, annual
    price_points: Dict[str, AgentPricePoint] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "ProductPricing":
        price_points = {}
        if data.get("pricePoints"):
            for currency, pp_data in data["pricePoints"].items():
                price_points[currency] = AgentPricePoint.from_dict(pp_data)
        return cls(
            event_name=data.get("eventName", data.get("event_name", "")),
            taxable=data.get("taxable", True),
            credit_cost=data.get("creditCost", data.get("credit_cost")),
            charge_type=data.get("chargeType", data.get("charge_type", "usage")),
            pricing_model=data.get("pricingModel", data.get("pricing_model", "PerUnit")),
            billing_frequency=data.get("billingFrequency", data.get("billing_frequency", "monthly")),
            price_points=price_points,
        )

    def to_dict(self) -> dict:
        result = {
            "eventName": self.event_name,
            "taxable": self.taxable,
            "chargeType": self.charge_type,
            "pricingModel": self.pricing_model,
            "billingFrequency": self.billing_frequency,
            "pricePoints": {k: v.to_dict() for k, v in self.price_points.items()},
        }
        if self.credit_cost is not None:
            result["creditCost"] = self.credit_cost
        return result


@dataclass
class ProductAttribute:
    """
    Product attribute with pricing configuration.

    Maps to Paid AI's AgentAttribute in the Product schema.
    """
    name: str = ""
    active: bool = True
    pricing: Optional[ProductPricing] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ProductAttribute":
        pricing = None
        if data.get("pricing"):
            pricing = ProductPricing.from_dict(data["pricing"])
        return cls(
            name=data.get("name", ""),
            active=data.get("active", True),
            pricing=pricing,
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "active": self.active,
            "pricing": self.pricing.to_dict() if self.pricing else None,
        }


@dataclass
class Product:
    """
    Represents a product in Alura.

    Maps to Paid AI's Product schema. Products are billable items
    (formerly called agents) that customers purchase.
    """
    id: Optional[str] = None
    external_id: Optional[str] = None
    display_id: str = ""
    organization_id: Optional[str] = None
    name: str = ""
    description: Optional[str] = None
    type: str = "agent"  # agent, product, prepaidCreditBundle
    active: bool = True
    product_code: Optional[str] = None
    product_attributes: List[ProductAttribute] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Create Product from API response"""
        product_attributes = []
        if data.get("ProductAttribute"):
            product_attributes = [ProductAttribute.from_dict(a) for a in data["ProductAttribute"]]

        def parse_dt(value):
            if not value:
                return None
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            return None

        return cls(
            id=str(data.get("id")) if data.get("id") else None,
            external_id=data.get("externalId", data.get("external_id")),
            display_id=data.get("displayId", data.get("display_id", "")),
            organization_id=data.get("organizationId", data.get("organization_id")),
            name=data.get("name", ""),
            description=data.get("description"),
            type=data.get("type", "agent"),
            active=data.get("active", True),
            product_code=data.get("productCode", data.get("product_code")),
            product_attributes=product_attributes,
            metadata=data.get("metadata", {}),
            created_at=parse_dt(data.get("createdAt", data.get("created_at"))),
            updated_at=parse_dt(data.get("updatedAt", data.get("updated_at"))),
        )

    def to_dict(self) -> dict:
        """Convert to API payload for create/update."""
        result = {
            "name": self.name,
        }
        if self.description:
            result["description"] = self.description
        if self.type:
            result["type"] = self.type
        if self.external_id:
            result["externalId"] = self.external_id
        if self.product_code:
            result["productCode"] = self.product_code
        if self.metadata:
            result["metadata"] = self.metadata
        return result
