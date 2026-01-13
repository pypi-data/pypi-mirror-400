"""
Alura Python SDK - AI Usage Tracking & Billing
"""
from .client import Alura, AluraError, AuthenticationError, APIError
from .wrappers import AluraOpenAI
from .models import (
    Action,
    Signal,  # Backward compatibility alias for Action
    Customer,
    Contact,
    Order,
    OrderLine,
    OrderLineAttribute,
    OrderLineAttributePricing,
    PricePoint,
    Tier,
    Address,
    # Product Models (Paid AI compatible)
    Product,
    ProductType,
    ProductAttribute,
    ProductPricing,
    AgentPricePoint,
    AgentPricePointTiers,
    # Entitlement/Credit Bundle Models (Paid AI compatible)
    EntitlementUsage,
    # Cost Trace Models (Paid AI compatible)
    CostAmount,
    CostTrace,
    CostTracesResponse,
    # Usage Summary Models (Paid AI compatible)
    UsageSummary,
    UsageSummaryOrder,
    UsageSummaryOrderLine,
    UsageSummariesResponse,
    # Enums (Paid AI compatible)
    ChargeType,
    PricingModelType,
    BillingFrequency,
    CreationState,
    Currency,
    TaxExemptStatus,
    CreationSource,
)

__version__ = "0.3.5"
__all__ = [
    # Client
    "Alura",
    "AluraOpenAI",
    "AluraError",
    "AuthenticationError",
    "APIError",
    # Core Models
    "Signal",  # Deprecated, use Action
    "Action",  # Alias for Signal
    "Customer",
    "Contact",
    "Address",
    # Product Models (Paid AI compatible)
    "Product",
    "ProductType",
    "ProductAttribute",
    "ProductPricing",
    "AgentPricePoint",
    "AgentPricePointTiers",
    # Order Models (Paid AI compatible)
    "Order",
    "OrderLine",
    "OrderLineAttribute",
    "OrderLineAttributePricing",
    "PricePoint",
    "Tier",
    # Entitlement/Credit Bundle Models (Paid AI compatible)
    "EntitlementUsage",
    # Cost Trace Models (Paid AI compatible)
    "CostAmount",
    "CostTrace",
    "CostTracesResponse",
    # Usage Summary Models (Paid AI compatible)
    "UsageSummary",
    "UsageSummaryOrder",
    "UsageSummaryOrderLine",
    "UsageSummariesResponse",
    # Enums
    "ChargeType",
    "PricingModelType",
    "BillingFrequency",
    "CreationState",
    "Currency",
    "TaxExemptStatus",
    "CreationSource",
]
