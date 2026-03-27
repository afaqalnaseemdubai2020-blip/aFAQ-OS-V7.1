"""Shopify Router — Sync, Reports, Analytics"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date

from app.modules.shopify.config import config
from app.modules.shopify.sync import sync
from app.modules.shopify.crud import orders, customers, products, analytics
from app.modules.shopify.models import SyncRequest

shopify_router = APIRouter(prefix="/api/shopify", tags=["🛒 Shopify"])

# ── SYNC ───────────────────────────────
@shopify_router.post("/sync/all")
async def full_sync(since: Optional[date] = None):
    """Full sync: orders + customers + products"""
    return await sync.full_sync(since=since)

@shopify_router.post("/sync/orders")
async def sync_orders(since: Optional[date] = None, until: Optional[date] = None):
    return await sync.sync_orders(since=since, until=until)

@shopify_router.post("/sync/customers")
async def sync_customers():
    return await sync.sync_customers()

@shopify_router.post("/sync/products")
async def sync_products():
    return await sync.sync_products()

@shopify_router.get("/sync/status")
async def sync_status():
    return {
        "configured": config.is_configured,
        "store_url": config.store_url or "NOT SET",
        "counts": {
            "orders": orders.count(),
            "customers": customers.count(),
            "products": products.count()
        }
    }

# ── PILLAR 1: FINANCIAL ───────────────
@shopify_router.get("/reports/sales")
async def sales_report(since: Optional[date] = None, until: Optional[date] = None):
    """Sales performance: revenue, AOV, margins, channel breakdown"""
    return analytics.sales_metrics(since=since, until=until)

@shopify_router.get("/reports/revenue-trend")
async def revenue_trend():
    """Monthly revenue trend (last 12 months)"""
    from datetime import datetime, timedelta
    trends = []
    now = datetime.now()
    for i in range(12):
        month_start = (now.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        if i == 0:
            month_end = now.date()
        else:
            month_end = (now.replace(day=1) - timedelta(days=30*(i-1))).replace(day=1)
        m = analytics.sales_metrics(since=month_start.date(), until=month_end)
        trends.append({"month": month_start.strftime("%Y-%m"), "revenue": m["total_revenue"], "orders": m["total_orders"]})
    return {"trends": list(reversed(trends))}

# ── PILLAR 2: CUSTOMER ────────────────
@shopify_router.get("/reports/customers")
async def customer_report():
    """Customer health: retention, LTV, churn"""
    return analytics.customer_metrics()

@shopify_router.get("/reports/rfm")
async def rfm_report(limit: int = Query(50, ge=1, le=500)):
    """RFM segmentation: Champions, Loyal, At Risk, Lost"""
    return analytics.rfm_analysis(limit=limit)

@shopify_router.get("/reports/customer-ltv")
async def customer_ltv():
    """Top customers by lifetime value"""
    cs = customers.list(limit=50)
    return {"top_customers": cs}

# ── PILLAR 3: MARKETING ───────────────
@shopify_router.get("/reports/marketing")
async def marketing_report():
    """Channel attribution & marketing efficiency"""
    return analytics.marketing_metrics()

# ── PILLAR 4: INVENTORY ───────────────
@shopify_router.get("/reports/inventory")
async def inventory_report():
    """ABC analysis, sell-through, reorder alerts"""
    return analytics.inventory_analysis()

@shopify_router.get("/reports/reorder-alerts")
async def reorder_alerts():
    """Products needing reorder"""
    items = analytics.inventory_analysis()
    return [i for i in items if i.get("reorder_recommended")]

# ── FULL DASHBOARD ────────────────────
@shopify_router.get("/dashboard")
async def full_dashboard():
    """Complete manager dashboard — all 4 pillars"""
    return analytics.full_dashboard()

# ── DATA ENDPOINTS ────────────────────
@shopify_router.get("/orders")
async def list_orders(status: Optional[str] = None, since: Optional[date] = None, limit: int = 50):
    return orders.list(status=status, since=since, limit=limit)

@shopify_router.get("/customers")
async def list_customers(min_orders: int = 0, limit: int = 50):
    return customers.list(min_orders=min_orders, limit=limit)

@shopify_router.get("/products")
async def list_products(limit: int = 50):
    return products.list(limit=limit)

# ── SEED DATA (demo) ──────────────────
@shopify_router.post("/demo/seed")
async def seed_demo():
    """Seed demo data for testing"""
    from datetime import datetime, timedelta
    import random
    
    # Demo customers
    demo_customers = []
    for i in range(25):
        demo_customers.append({
            "shopify_id": 1000 + i,
            "email": f"customer{i}@example.com",
            "first_name": f"Customer",
            "last_name": f"{i+1}",
            "phone": f"+97150{random.randint(1000000, 9999999)}",
            "orders_count": random.randint(0, 15),
            "total_spent": round(random.uniform(100, 15000), 2),
            "tags": random.choice([["vip"], ["wholesale"], ["retail"], []]),
            "created_at": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
            "updated_at": datetime.now().isoformat()
        })
    
    # Demo products
    demo_products = []
    product_names = [
        "Babyliss Pro Nano Titanium", "Wahl Senior Cordless", "Dyson Supersonic",
        "Olaplex No.3", "Moroccanoil Treatment", "GHD Platinum+", "T3 Micro Wand",
        "Kérastase Bain Satin", "Schwarzkopf IGORA", "Redken Extreme",
        "Paul Mitchell Tea Tree", "CHI Original", "Revlon One-Step", "Conair InfinitiPro"
    ]
    for i, name in enumerate(product_names):
        qty = random.randint(0, 200)
        demo_products.append({
            "shopify_id": 2000 + i,
            "title": name,
            "vendor": name.split()[0],
            "product_type": random.choice(["Hair Tools", "Hair Care", "Styling"]),
            "variants": [{"id": 3000+i, "sku": f"SKU-{i+1:03d}", "price": str(random.randint(50, 800)), "inventory_quantity": qty}],
            "inventory_quantity": qty,
            "price": random.randint(50, 800),
            "status": "active",
            "created_at": (datetime.now() - timedelta(days=random.randint(90, 365))).isoformat(),
            "updated_at": datetime.now().isoformat()
        })
    
    # Demo orders
    demo_orders = []
    for i in range(100):
        cust = random.choice(demo_customers)
        items = []
        for _ in range(random.randint(1, 4)):
            prod = random.choice(demo_products)
            qty = random.randint(1, 5)
            price = prod["price"]
            items.append({
                "product_id": prod["shopify_id"],
                "title": prod["title"],
                "quantity": qty,
                "price": price,
                "discount": 0,
                "total": price * qty,
                "sku": prod["variants"][0]["sku"]
            })
        subtotal = sum(i["total"] for i in items)
        discount = round(subtotal * random.uniform(0, 0.15), 2)
        
        demo_orders.append({
            "shopify_id": 5000 + i,
            "order_number": f"#{1001+i}",
            "email": cust["email"],
            "customer_id": cust["shopify_id"],
            "financial_status": random.choice(["paid", "paid", "paid", "pending", "refunded"]),
            "fulfillment_status": random.choice(["fulfilled", "fulfilled", "partial", None]),
            "total_price": round(subtotal - discount, 2),
            "subtotal_price": subtotal,
            "total_tax": round(subtotal * 0.05, 2),
            "total_discounts": discount,
            "total_shipping": random.choice([0, 15, 25, 0]),
            "currency": "AED",
            "items": items,
            "channel": random.choice(["online_store", "online_store", "pos", "shop_app", "facebook"]),
            "created_at": (datetime.now() - timedelta(days=random.randint(0, 180))).isoformat(),
            "updated_at": datetime.now().isoformat()
        })
    
    # Save all
    customers.bulk_upsert(demo_customers)
    products.bulk_upsert(demo_products)
    orders.bulk_upsert(demo_orders)
    
    return {
        "seeded": {
            "customers": len(demo_customers),
            "products": len(demo_products),
            "orders": len(demo_orders)
        },
        "message": "Demo data seeded. Try GET /api/shopify/dashboard"
    }
