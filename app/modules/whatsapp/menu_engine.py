"""Sophisticated WhatsApp menu engine with AI fallback (DeepSeek)."""
from __future__ import annotations

import json
import os
from typing import Dict, List

from app.modules.whatsapp.ai_provider import generate_ai_response
from app.modules.whatsapp.training import training


_STATE: Dict[str, dict] = {}


def _session(phone: str, name: str = "Guest") -> dict:
    if phone not in _STATE:
        _STATE[phone] = {
            "name": name or "Guest",
            "menu": "main",
            "awaiting": None,
        }
    if name:
        _STATE[phone]["name"] = name
    return _STATE[phone]


def _is_arabic(text: str) -> bool:
    return any("\u0600" <= c <= "\u06FF" for c in text)


def _main_menu(name: str = "Guest") -> str:
    return (
        f"🏠 *Welcome to AFAQ Store, {name}!*\n"
        "Official UAE Distributor of ENZO & Lizze\n\n"
        "*1*. 🛍️ Browse Products\n"
        "*2*. 💰 Get Prices\n"
        "*3*. 📦 Track My Order\n"
        "*4*. 🏪 Store Info\n"
        "*5*. 🤝 Talk to Human\n"
        "*6*. 📋 Wholesale Inquiry\n\n"
        "_Reply with a number to continue_"
    )


def _products_menu() -> str:
    return (
        "🛍️ *Browse Products*\n"
        "Choose a category:\n\n"
        "*1*. ⭐ Best Sellers\n"
        "*2*. ✂️ Hair Dryers\n"
        "*3*. 🔥 Hair Straighteners\n"
        "*4*. 🧹 Trimmers & Clippers\n"
        "*5*. 🔍 Search by Brand\n"
        "*6*. 💬 Product Advisor (AI)\n"
        "*0*. ↩️ Back to Main Menu\n\n"
        "_Reply with a number to continue_"
    )


def _brand_menu() -> str:
    return (
        "🔍 *Search by Brand*\n\n"
        "*1*. ENZO Professional\n"
        "*2*. Lizze Professional\n"
        "*3*. Wahl\n"
        "*4*. Babyliss\n"
        "*5*. Philips\n"
        "*6*. Braun\n"
        "*0*. ↩️ Back\n\n"
        "_Reply with a number to continue_"
    )


def _prices_menu() -> str:
    return (
        "💰 *Pricing Menu*\n\n"
        "*1*. Retail Prices\n"
        "*2*. Wholesale Prices\n"
        "*3*. Current Offers\n"
        "*4*. Price List (PDF request)\n"
        "*0*. ↩️ Back to Main Menu\n\n"
        "_Reply with a number to continue_"
    )


def _store_info() -> str:
    return (
        "🏪 *AFAQ Store Info*\n\n"
        "📍 Deira, Dubai, UAE\n"
        "📞 +971581778894\n"
        "📧 info@afaqalnaseem.com\n"
        "🌐 www.afaqalnaseem.com\n\n"
        "🕒 Sun-Thu: 9AM-10PM\n"
        "🕒 Fri-Sat: 10AM-11PM\n\n"
        "Type *menu* to go back."
    )


def _offers_text() -> str:
    return (
        "🔥 *Current Offers*\n"
        "• Free shipping over AED 200\n"
        "• Selected tools up to 15% off\n"
        "• Bulk buyers get special B2B rates\n\n"
        "For exact live offers, reply with product name or type *5* for human agent."
    )


def _load_products() -> List[dict]:
    fp = os.path.join("data", "shopify", "products.json")
    if not os.path.exists(fp):
        return []
    try:
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def _product_lines(items: List[dict], limit: int = 6) -> str:
    if not items:
        return "No products found right now."
    lines: List[str] = []
    for i, p in enumerate(items[:limit], start=1):
        title = (p.get("title") or "Unknown Product").strip()
        variants = p.get("variants") or []
        price = variants[0].get("price") if variants else None
        lines.append(f"{i}. {title[:55]}" + (f" — AED {price}" if price else ""))
    if len(items) > limit:
        lines.append(f"_...and {len(items) - limit} more products_")
    return "\n".join(lines)


def _filter_products(keyword: str) -> List[dict]:
    kw = keyword.lower().strip()
    if not kw:
        return []
    products = _load_products()
    return [
        p
        for p in products
        if kw in (p.get("title", "").lower())
        or kw in (p.get("vendor", "").lower())
        or kw in (p.get("product_type", "").lower())
    ]


def _category_reply(category_key: str, label: str) -> str:
    items = _filter_products(category_key)
    return (
        f"🛍️ *{label}*\n\n"
        f"{_product_lines(items)}\n\n"
        "Type a product name for details, or *menu* to return to main menu."
    )


async def process_message(phone: str, message: str, name: str = "Guest") -> str:
    """Main chat orchestration: menus first, AI fallback second."""
    text = (message or "").strip()
    lowered = text.lower()
    state = _session(phone, name)

    if lowered in {"menu", "start", "main", "0", "hello", "hi", "مرحبا", "السلام عليكم"}:
        state["menu"] = "main"
        state["awaiting"] = None
        return _main_menu(state.get("name") or "Guest")

    if lowered in {"back", "رجوع", "عودة"}:
        state["menu"] = "main"
        state["awaiting"] = None
        return _main_menu(state.get("name") or "Guest")

    if state.get("awaiting") == "order_number":
        state["awaiting"] = None
        state["menu"] = "main"
        return (
            f"📦 Thanks! We received order number: *{text}*\n"
            "Our team will verify and update you shortly.\n\n"
            "Type *menu* for more options."
        )

    if state.get("awaiting") == "product_advisor":
        state["awaiting"] = None
        ai = await generate_ai_response(
            f"Customer needs product advice. Message: {text}. Provide concise recommendation and ask 1 follow-up question."
        )
        if ai:
            return ai

    # Menu handling
    menu = state.get("menu", "main")
    if menu == "main":
        if text == "1":
            state["menu"] = "products"
            return _products_menu()
        if text == "2":
            state["menu"] = "prices"
            return _prices_menu()
        if text == "3":
            state["awaiting"] = "order_number"
            return "📦 Please share your order number (example: #1045)."
        if text == "4":
            return _store_info()
        if text == "5":
            return (
                "🤝 *Connecting to Human Agent*\n"
                "We are escalating your request now. Please wait — our team will reply shortly."
            )
        if text == "6":
            return (
                "📋 *Wholesale Inquiry*\n"
                "Great choice. We offer special B2B pricing (20–30% depending on volume).\n"
                "Please share:\n"
                "1) Product type\n2) Quantity\n3) Delivery city\n\n"
                "Or type *5* to connect to a human agent now."
            )

    if menu == "products":
        if text == "1":
            return _category_reply("enzo", "Best Sellers")
        if text == "2":
            return _category_reply("dryer", "Hair Dryers")
        if text == "3":
            return _category_reply("straight", "Hair Straighteners")
        if text == "4":
            return _category_reply("clipper", "Trimmers & Clippers")
        if text == "5":
            state["menu"] = "brands"
            return _brand_menu()
        if text == "6":
            state["awaiting"] = "product_advisor"
            return "💬 Tell me your hair type, desired result, and budget (AED), and I’ll recommend the best tool."

    if menu == "brands":
        brand_map = {
            "1": ("enzo", "ENZO Professional"),
            "2": ("lizze", "Lizze Professional"),
            "3": ("wahl", "Wahl"),
            "4": ("babyliss", "Babyliss"),
            "5": ("philips", "Philips"),
            "6": ("braun", "Braun"),
        }
        if text in brand_map:
            kw, label = brand_map[text]
            return _category_reply(kw, label)

    if menu == "prices":
        if text == "1":
            return "💰 Retail prices vary by model. Send product name (e.g., ENZO dryer 8801) and I’ll fetch details."
        if text == "2":
            return "📦 Wholesale pricing starts from quantity tiers. Share your required quantity and model."
        if text == "3":
            return _offers_text()
        if text == "4":
            return "📄 We can send the latest price list PDF via agent. Type *5* from main menu to request it."

    # Template/training engine fallback
    training_result = training.get_response(text)
    if training_result.get("confidence", 0) >= 0.72 and training_result.get("response"):
        return training_result["response"]

    # DeepSeek smart fallback
    ai_response = await generate_ai_response(
        f"Customer asked: {text}. Reply as AFAQ WhatsApp assistant. Keep concise and actionable."
    )
    if ai_response:
        return ai_response

    # Final fallback: return current menu context
    if _is_arabic(text):
        return "لم أفهم طلبك بالكامل. اكتب *menu* لعرض القائمة الرئيسية أو اشرح سؤالك بشكل أبسط."
    return "I didn’t fully catch that. Type *menu* to open the main options, or ask in another way."
