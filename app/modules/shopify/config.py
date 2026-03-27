"""Shopify API Configuration"""
import os
from dataclasses import dataclass, field

@dataclass
class ShopifyConfig:
    store_url: str = field(default_factory=lambda: os.getenv("SHOPIFY_STORE_URL", ""))
    api_key: str = field(default_factory=lambda: os.getenv("SHOPIFY_API_KEY", ""))
    api_secret: str = field(default_factory=lambda: os.getenv("SHOPIFY_API_SECRET", ""))
    access_token: str = field(default_factory=lambda: os.getenv("SHOPIFY_ACCESS_TOKEN", ""))
    api_version: str = field(default_factory=lambda: os.getenv("SHOPIFY_API_VERSION", "2024-01"))
    
    @property
    def base_url(self) -> str:
        url = self.store_url.replace("https://", "").replace("http://", "").rstrip("/")
        return f"https://{url}/admin/api/{self.api_version}"
    
    @property
    def headers(self) -> dict:
        return {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
    
    @property
    def is_configured(self) -> bool:
        return bool(self.access_token and self.store_url)

config = ShopifyConfig()
