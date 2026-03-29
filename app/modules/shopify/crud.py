"""Shopify CRUD — Local data store for synced Shopify data"""
import json, os
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from app.modules.shopify.models import (
    Order, Customer, Product, OrderItem, 
    SalesMetrics, CustomerMetrics, RFMProfile, 
    InventoryItem, MarketingMetrics
)

DATA_DIR = "data/shopify"
os.makedirs(DATA_DIR, exist_ok=True)

def _load(entity: str) -> List[dict]:
    fp = os.path.join(DATA_DIR, f"{entity}.json")
    if os.path.exists(fp):
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def _save(entity: str, data: list):
    fp = os.path.join(DATA_DIR, f"{entity}.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

# ── ORDER CRUD ─────────────────────────
class OrderCRUD:
    entity = "orders"
    
    def list(self, status: Optional[str] = None, 
             since: Optional[date] = None,
             until: Optional[date] = None,
             limit: int = 100) -> List[dict]:
        data = _load(self.entity)
        if status:
            data = [d for d in data if d.get("financial_status") == status]
        if since:
            data = [d for d in data if d.get("created_at","")[:10] >= str(since)]
        if until:
            data = [d for d in data if d.get("created_at","")[:10] <= str(until)]
        return sorted(data, key=lambda x: x.get("created_at",""), reverse=True)[:limit]
    
    def upsert(self, order: dict) -> dict:
        data = _load(self.entity)
        for i, d in enumerate(data):
            if d.get("shopify_id") == order.get("shopify_id"):
                data[i] = order
                _save(self.entity, data)
                return order
        data.append(order)
        _save(self.entity, data)
        return order
    
    def bulk_upsert(self, orders: List[dict]) -> int:
        data = _load(self.entity)
        existing = {d.get("shopify_id"): i for i, d in enumerate(data)}
        count = 0
        for o in orders:
            sid = o.get("shopify_id")
            if sid in existing:
                data[existing[sid]] = o
            else:
                data.append(o)
            count += 1
        _save(self.entity, data)
        return count
    
    def get(self, shopify_id: int) -> Optional[dict]:
        return next((d for d in _load(self.entity) if d.get("shopify_id") == shopify_id), None)
    
    def count(self) -> int:
        return len(_load(self.entity))

# ── CUSTOMER CRUD ──────────────────────
class CustomerCRUD:
    entity = "customers"
    
    def list(self, min_orders: int = 0, limit: int = 100) -> List[dict]:
        data = _load(self.entity)
        data = [d for d in data if d.get("orders_count", 0) >= min_orders]
        return sorted(data, key=lambda x: x.get("total_spent", 0), reverse=True)[:limit]
    
    def upsert(self, customer: dict) -> dict:
        data = _load(self.entity)
        for i, d in enumerate(data):
            if d.get("shopify_id") == customer.get("shopify_id"):
                data[i] = customer
                _save(self.entity, data)
                return customer
        data.append(customer)
        _save(self.entity, data)
        return customer
    
    def bulk_upsert(self, customers: List[dict]) -> int:
        data = _load(self.entity)
        existing = {d.get("shopify_id"): i for i, d in enumerate(data)}
        count = 0
        for c in customers:
            sid = c.get("shopify_id")
            if sid in existing:
                data[existing[sid]] = c
            else:
                data.append(c)
            count += 1
        _save(self.entity, data)
        return count
    
    def get(self, shopify_id: int) -> Optional[dict]:
        return next((d for d in _load(self.entity) if d.get("shopify_id") == shopify_id), None)
    
    def count(self) -> int:
        return len(_load(self.entity))

# ── PRODUCT CRUD ───────────────────────
class ProductCRUD:
    entity = "products"
    
    def list(self, status: str = "active", limit: int = 100) -> List[dict]:
        data = _load(self.entity)
        if status:
            data = [d for d in data if d.get("status") == status]
        return sorted(data, key=lambda x: x.get("inventory_quantity", 0))[:limit]
    
    def upsert(self, product: dict) -> dict:
        data = _load(self.entity)
        for i, d in enumerate(data):
            if d.get("shopify_id") == product.get("shopify_id"):
                data[i] = product
                _save(self.entity, data)
                return product
        data.append(product)
        _save(self.entity, data)
        return product
    
    def bulk_upsert(self, products: List[dict]) -> int:
        data = _load(self.entity)
        existing = {d.get("shopify_id"): i for i, d in enumerate(data)}
        count = 0
        for p in products:
            sid = p.get("shopify_id")
            if sid in existing:
                data[existing[sid]] = p
            else:
                data.append(p)
            count += 1
        _save(self.entity, data)
        return count
    
    def count(self) -> int:
        return len(_load(self.entity))

# ── ANALYTICS ENGINE ──────────────────
class AnalyticsEngine:
    def __init__(self):
        self.orders = OrderCRUD()
        self.customers = CustomerCRUD()
        self.products = ProductCRUD()
    
    def sales_metrics(self, since: Optional[date] = None, until: Optional[date] = None) -> Dict:
        """Pillar 1: Financial Health & Profitability"""
        orders = self.orders.list(since=since, until=until, limit=10000)
        
        total_revenue = sum(o.get("total_price", 0) for o in orders)
        total_orders = len(orders)
        aov = total_revenue / total_orders if total_orders > 0 else 0
        total_discounts = sum(o.get("total_discounts", 0) for o in orders)
        total_tax = sum(o.get("total_tax", 0) for o in orders)
        
        # Channel breakdown
        channels = {}
        for o in orders:
            ch = o.get("channel") or "online_store"
            channels[ch] = channels.get(ch, 0) + o.get("total_price", 0)
        
        # Top products
        product_revenue = {}
        for o in orders:
            for item in o.get("items", []):
                pid = item.get("title", "Unknown")
                product_revenue[pid] = product_revenue.get(pid, 0) + item.get("total", 0)
        top_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:10]
        
        period_str = f"{since or 'all'} to {until or 'now'}"
        
        return {
            "period": period_str,
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "avg_order_value": round(aov, 2),
            "total_discounts": round(total_discounts, 2),
            "total_tax": round(total_tax, 2),
            "currency": "AED",
            "orders_by_channel": {k: round(v, 2) for k, v in sorted(channels.items(), key=lambda x: x[1], reverse=True)},
            "top_products": [{"title": k, "revenue": round(v, 2)} for k, v in top_products]
        }
    
    def customer_metrics(self) -> Dict:
        """Pillar 2: Customer Retention & Lifetime Value"""
        customers = self.customers.list(limit=10000)
        orders = self.orders.list(limit=10000)
        
        total_customers = len(customers)
        
        # Returning vs new
        returning = len([c for c in customers if c.get("orders_count", 0) > 1])
        returning_rate = (returning / total_customers * 100) if total_customers > 0 else 0
        
        # LTV
        avg_ltv = sum(c.get("total_spent", 0) for c in customers) / total_customers if total_customers > 0 else 0
        
        # Churn risk (no order in 90 days)
        cutoff = (datetime.now() - timedelta(days=90)).isoformat()
        active_ids = set(o.get("customer_id") for o in orders if o.get("created_at", "") > cutoff)
        churn_risk = len([c for c in customers if c.get("shopify_id") not in active_ids and c.get("orders_count", 0) > 1])
        
        # Champions (high LTV + recent)
        champions = len([c for c in customers if c.get("total_spent", 0) > avg_ltv * 2 and c.get("shopify_id") in active_ids])
        
        return {
            "total_customers": total_customers,
            "returning_count": returning,
            "returning_rate": round(returning_rate, 1),
            "avg_ltv": round(avg_ltv, 2),
            "churn_risk_count": churn_risk,
            "champions_count": champions
        }
    
    def rfm_analysis(self, limit: int = 50) -> List[Dict]:
        """RFM Segmentation"""
        customers = self.customers.list(limit=10000)
        orders = self.orders.list(limit=10000)
        
        if not customers:
            return []
        
        now = datetime.now()
        rfm_data = []
        
        for c in customers:
            cid = c.get("shopify_id")
            cust_orders = [o for o in orders if o.get("customer_id") == cid]
            
            if not cust_orders:
                continue
            
            # Recency
            last_order = max(cust_orders, key=lambda x: x.get("created_at", ""))
            last_date = last_order.get("created_at", "")[:10]
            try:
                recency = (now - datetime.fromisoformat(last_date)).days
            except:
                recency = 999
            
            frequency = len(cust_orders)
            monetary = c.get("total_spent", 0)
            
            rfm_data.append({
                "customer_id": cid,
                "email": c.get("email"),
                "name": f"{c.get('first_name','')} {c.get('last_name','')}".strip(),
                "recency_days": recency,
                "frequency": frequency,
                "monetary": round(monetary, 2)
            })
        
        if not rfm_data:
            return []
        
        # Score R/F/M (1-5)
        sorted_by_r = sorted(rfm_data, key=lambda x: x["recency_days"])
        sorted_by_f = sorted(rfm_data, key=lambda x: x["frequency"], reverse=True)
        sorted_by_m = sorted(rfm_data, key=lambda x: x["monetary"], reverse=True)
        
        n = len(rfm_data)
        for i, d in enumerate(rfm_data):
            for j, s in enumerate(sorted_by_r):
                if s["customer_id"] == d["customer_id"]:
                    d["r_score"] = min(5, (j * 5 // n) + 1)
                    break
            for j, s in enumerate(sorted_by_f):
                if s["customer_id"] == d["customer_id"]:
                    d["f_score"] = min(5, (j * 5 // n) + 1)
                    break
            for j, s in enumerate(sorted_by_m):
                if s["customer_id"] == d["customer_id"]:
                    d["m_score"] = min(5, (j * 5 // n) + 1)
                    break
            
            # Segment
            total = d["r_score"] + d["f_score"] + d["m_score"]
            if total >= 13:
                d["segment"] = "champion"
            elif total >= 10:
                d["segment"] = "loyal"
            elif total >= 8:
                d["segment"] = "potential"
            elif total >= 6:
                d["segment"] = "new"
            elif d["r_score"] <= 2:
                d["segment"] = "at_risk" if d["m_score"] >= 3 else "lost"
            else:
                d["segment"] = "needs_attention"
        
        return sorted(rfm_data, key=lambda x: x["monetary"], reverse=True)[:limit]
    
    def inventory_analysis(self) -> List[Dict]:
        """Pillar 4: ABC Analysis + Sell-through + Days of stock"""
        products = self.products.list(limit=10000)
        orders = self.orders.list(limit=10000)
        
        # Revenue per product
        product_revenue = {}
        for o in orders:
            for item in o.get("items", []):
                pid = item.get("product_id")
                if pid:
                    product_revenue[pid] = product_revenue.get(pid, 0) + item.get("total", 0)
        
        total_revenue = sum(product_revenue.values()) or 1
        
        # Sort by revenue for ABC
        sorted_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)
        cumulative = 0
        abc_map = {}
        for pid, rev in sorted_products:
            cumulative += rev
            pct = cumulative / total_revenue
            if pct <= 0.80:
                abc_map[pid] = "A"
            elif pct <= 0.95:
                abc_map[pid] = "B"
            else:
                abc_map[pid] = "C"
        
        results = []
        for p in products:
            pid = p.get("shopify_id")
            qty = p.get("inventory_quantity", 0)
            rev = product_revenue.get(pid, 0)
            
            # Sell-through (orders in last 30 days / stock)
            recent_orders = [o for o in orders 
                           if o.get("created_at", "") > (datetime.now() - timedelta(days=30)).isoformat()]
            sold_30d = sum(
                item.get("quantity", 0) 
                for o in recent_orders 
                for item in o.get("items", []) 
                if item.get("product_id") == pid
            )
            sell_through = (sold_30d / qty * 100) if qty > 0 else 0
            daily_rate = sold_30d / 30
            days_of_stock = int(qty / daily_rate) if daily_rate > 0 else 999
            
            results.append({
                "product_id": pid,
                "title": p.get("title"),
                "sku": (p.get("variants") or [{}])[0].get("sku") if p.get("variants") else None,
                "quantity": qty,
                "abc_class": abc_map.get(pid, "C"),
                "revenue_contribution": round(rev, 2),
                "sell_through_rate": round(sell_through, 1),
                "days_of_stock": days_of_stock,
                "reorder_recommended": days_of_stock < 14 and abc_map.get(pid) in ["A", "B"]
            })
        
        return sorted(results, key=lambda x: x["revenue_contribution"], reverse=True)
    
    def marketing_metrics(self) -> Dict:
        """Pillar 3: Marketing Efficiency — Channel attribution"""
        orders = self.orders.list(limit=10000)
        
        channel_revenue = {}
        channel_orders = {}
        for o in orders:
            ch = o.get("channel") or "online_store"
            channel_revenue[ch] = channel_revenue.get(ch, 0) + o.get("total_price", 0)
            channel_orders[ch] = channel_orders.get(ch, 0) + 1
        
        return {
            "channel_revenue": {k: round(v, 2) for k, v in sorted(channel_revenue.items(), key=lambda x: x[1], reverse=True)},
            "channel_orders": channel_orders,
            "total_channels": len(channel_revenue)
        }
    
    def full_dashboard(self) -> Dict:
        """Complete manager dashboard"""
        return {
            "financial": self.sales_metrics(),
            "customers": self.customer_metrics(),
            "top_rfm": self.rfm_analysis(limit=10),
            "inventory_alerts": [i for i in self.inventory_analysis() if i.get("reorder_recommended")],
            "marketing": self.marketing_metrics(),
            "generated_at": datetime.now().isoformat()
        }

# ── INSTANCES ──────────────────────────
orders = OrderCRUD()
customers = CustomerCRUD()
products = ProductCRUD()
analytics = AnalyticsEngine()
