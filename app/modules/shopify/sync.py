"""Shopify Sync Service — Pull data from Shopify API"""
import json
import httpx
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from app.modules.shopify.config import config
from app.modules.shopify.crud import orders, customers, products

class ShopifySync:
    """Sync data from Shopify API to local store"""
    
    async def _fetch(self, endpoint: str, params: Dict = None) -> Dict:
        """Fetch from Shopify API"""
        if not config.is_configured:
            return {"error": "Shopify not configured", "hint": "Set SHOPIFY_ACCESS_TOKEN and SHOPIFY_STORE_URL"}
        
        url = f"{config.base_url}/{endpoint}.json"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=config.headers, params=params or {})
            if resp.status_code == 200:
                return resp.json()
            return {"error": resp.text, "status": resp.status_code}
    
    async def _fetch_all(self, endpoint: str, params: Dict = None, max_pages: int = 10) -> List[Dict]:
        """Fetch all pages from Shopify"""
        all_items = []
        params = params or {}
        params["limit"] = 250
        
        for page in range(1, max_pages + 1):
            params["page"] = page
            data = await self._fetch(endpoint, params)
            
            if "error" in data:
                break
            
            key = endpoint.split("/")[-1]
            items = data.get(key, [])
            
            if not items:
                break
            
            all_items.extend(items)
            
            if len(items) < 250:
                break
        
        return all_items
    
    # ── ORDERS ─────────────────────────
    async def sync_orders(self, since: Optional[date] = None, until: Optional[date] = None) -> Dict:
        """Pull orders from Shopify"""
        params = {}
        if since:
            params["created_at_min"] = since.isoformat() + "T00:00:00Z"
        if until:
            params["created_at_max"] = until.isoformat() + "T23:59:59Z"
        
        raw_orders = await self._fetch_all("orders", params)
        
        if isinstance(raw_orders, dict) and "error" in raw_orders:
            return raw_orders
        
        synced = []
        for o in raw_orders:
            items = []
            for li in o.get("line_items", []):
                items.append({
                    "product_id": li.get("product_id"),
                    "variant_id": li.get("variant_id"),
                    "title": li.get("title", ""),
                    "quantity": li.get("quantity", 0),
                    "price": float(li.get("price", 0)),
                    "discount": float(li.get("total_discount", 0)),
                    "total": float(li.get("price", 0)) * li.get("quantity", 0),
                    "sku": li.get("sku")
                })
            
            customer = o.get("customer") or {}
            
            order_data = {
                "shopify_id": o["id"],
                "order_number": o.get("name", ""),
                "email": o.get("email") or customer.get("email"),
                "customer_id": customer.get("id"),
                "financial_status": o.get("financial_status", "pending"),
                "fulfillment_status": o.get("fulfillment_status"),
                "total_price": float(o.get("total_price", 0)),
                "subtotal_price": float(o.get("subtotal_price", 0)),
                "total_tax": float(o.get("total_tax", 0)),
                "total_discounts": float(o.get("total_discounts", 0)),
                "total_shipping": sum(float(s.get("price", 0)) for s in o.get("shipping_lines", [])),
                "currency": o.get("currency", "AED"),
                "items": items,
                "channel": o.get("source_name"),
                "created_at": o.get("created_at"),
                "updated_at": o.get("updated_at"),
                "synced_at": datetime.now().isoformat()
            }
            synced.append(order_data)
        
        count = orders.bulk_upsert(synced)
        return {"synced": count, "total_orders": orders.count()}
    
    # ── CUSTOMERS ──────────────────────
    async def sync_customers(self) -> Dict:
        """Pull customers from Shopify"""
        raw = await self._fetch_all("customers")
        
        if isinstance(raw, dict) and "error" in raw:
            return raw
        
        synced = []
        for c in raw:
            cust_data = {
                "shopify_id": c["id"],
                "email": c.get("email"),
                "first_name": c.get("first_name"),
                "last_name": c.get("last_name"),
                "phone": c.get("phone"),
                "orders_count": c.get("orders_count", 0),
                "total_spent": float(c.get("total_spent", 0)),
                "tags": c.get("tags", "").split(",") if c.get("tags") else [],
                "verified_email": c.get("verified_email", False),
                "created_at": c.get("created_at"),
                "updated_at": c.get("updated_at")
            }
            synced.append(cust_data)
        
        count = customers.bulk_upsert(synced)
        return {"synced": count, "total_customers": customers.count()}
    
    # ── PRODUCTS ───────────────────────
    async def sync_products(self) -> Dict:
        """Pull products from Shopify"""
        raw = await self._fetch_all("products")
        
        if isinstance(raw, dict) and "error" in raw:
            return raw
        
        synced = []
        for p in raw:
            variants = p.get("variants", [])
            total_qty = sum(v.get("inventory_quantity", 0) for v in variants)
            min_price = min(float(v.get("price", 0)) for v in variants) if variants else 0
            
            prod_data = {
                "shopify_id": p["id"],
                "title": p.get("title"),
                "body_html": p.get("body_html"),
                "vendor": p.get("vendor"),
                "product_type": p.get("product_type"),
                "variants": [{"id": v["id"], "sku": v.get("sku"), "price": v.get("price"), 
                             "inventory_quantity": v.get("inventory_quantity", 0)} for v in variants],
                "inventory_quantity": total_qty,
                "price": min_price,
                "compare_at_price": variants[0].get("compare_at_price") if variants else None,
                "status": p.get("status"),
                "created_at": p.get("created_at"),
                "updated_at": p.get("updated_at")
            }
            synced.append(prod_data)
        
        count = products.bulk_upsert(synced)
        return {"synced": count, "total_products": products.count()}
    
    # ── FULL SYNC ──────────────────────
    async def full_sync(self, since: Optional[date] = None) -> Dict:
        """Sync everything"""
        results = {}
        results["orders"] = await self.sync_orders(since=since)
        results["customers"] = await self.sync_customers()
        results["products"] = await self.sync_products()
        return {"status": "completed", "results": results, "synced_at": datetime.now().isoformat()}

sync = ShopifySync()
