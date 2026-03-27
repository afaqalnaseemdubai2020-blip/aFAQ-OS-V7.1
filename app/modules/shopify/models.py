"""Shopify Data Models — Orders, Products, Customers, Inventory"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class SyncStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class OrderStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    ANY = "any"

# ── FINANCIAL MODELS ───────────────────
class OrderItem(BaseModel):
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    title: str
    quantity: int = 0
    price: float = 0.0
    discount: float = 0.0
    total: float = 0.0
    sku: Optional[str] = None

class Order(BaseModel):
    shopify_id: int
    order_number: str
    email: Optional[str] = None
    customer_id: Optional[int] = None
    financial_status: str = "pending"
    fulfillment_status: Optional[str] = None
    total_price: float = 0.0
    subtotal_price: float = 0.0
    total_tax: float = 0.0
    total_discounts: float = 0.0
    total_shipping: float = 0.0
    currency: str = "AED"
    items: List[OrderItem] = []
    channel: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    synced_at: Optional[datetime] = None

class Customer(BaseModel):
    shopify_id: int
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    orders_count: int = 0
    total_spent: float = 0.0
    tags: List[str] = []
    verified_email: bool = False
    created_at: datetime
    updated_at: datetime

class Product(BaseModel):
    shopify_id: int
    title: str
    body_html: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    variants: List[Dict[str, Any]] = []
    inventory_quantity: int = 0
    price: float = 0.0
    compare_at_price: Optional[float] = None
    status: str = "active"
    created_at: datetime
    updated_at: datetime

# ── ANALYTICS MODELS ──────────────────
class SalesMetrics(BaseModel):
    period: str
    total_revenue: float = 0.0
    total_orders: int = 0
    avg_order_value: float = 0.0
    gross_profit: float = 0.0
    net_profit: float = 0.0
    profit_margin: float = 0.0
    total_discounts: float = 0.0
    total_refunds: float = 0.0
    orders_by_channel: Dict[str, float] = {}
    top_products: List[Dict[str, Any]] = []

class CustomerMetrics(BaseModel):
    total_customers: int = 0
    new_customers: int = 0
    returning_rate: float = 0.0
    avg_ltv: float = 0.0
    churn_risk_count: int = 0
    champions_count: int = 0
    segments: Dict[str, int] = {}

class RFMSegment(str, Enum):
    CHAMPION = "champion"
    LOYAL = "loyal"
    POTENTIAL = "potential"
    NEW = "new"
    AT_RISK = "at_risk"
    LOST = "lost"

class RFMProfile(BaseModel):
    customer_id: int
    email: Optional[str]
    recency_days: int
    frequency: int
    monetary: float
    r_score: int = 0
    f_score: int = 0
    m_score: int = 0
    segment: str = "unknown"

class InventoryItem(BaseModel):
    product_id: int
    title: str
    sku: Optional[str] = None
    quantity: int = 0
    abc_class: str = "C"
    revenue_contribution: float = 0.0
    sell_through_rate: float = 0.0
    days_of_stock: int = 0
    reorder_recommended: bool = False

class MarketingMetrics(BaseModel):
    period: str
    sessions: int = 0
    conversion_rate: float = 0.0
    referrer_breakdown: Dict[str, int] = {}
    channel_revenue: Dict[str, float] = {}
    roas: Optional[float] = None

class SyncRequest(BaseModel):
    entities: List[str] = ["orders", "customers", "products"]
    since_date: Optional[date] = None
    until_date: Optional[date] = None
    force: bool = False
