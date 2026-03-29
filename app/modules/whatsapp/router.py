"""WhatsApp Bot Router - sophisticated menu + DeepSeek brain + bridge send."""
from datetime import datetime

from fastapi import APIRouter, Query, Request

from app.modules.whatsapp.classifier import classifier
from app.modules.whatsapp.menu_engine import process_message
from app.modules.whatsapp.session import session_manager
from app.modules.whatsapp.training import training
from app.modules.whatsapp.ultramsg import get_status, send_message

whatsapp_router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp Bot"])

# ============================================
# WEBHOOK - Receive from bridge
# ============================================

@whatsapp_router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Receive inbound WhatsApp and return reply text to bridge."""
    try:
        payload = await request.json()

        phone = payload.get("from", "")
        message_text = payload.get("body", "")
        contact_name = payload.get("pushname", "Guest")

        if not phone or not message_text:
            return {"reply": None}

        # Clean phone number
        phone = phone.replace("@c.us", "").replace("@g.us", "").replace("+", "")

        # Get/create session
        session = session_manager.get_session(phone)
        if not session:
            session = session_manager.create_session(phone, contact_name)

        session.last_activity = datetime.now()
        session.message_count += 1

        # Process via sophisticated menu engine (with AI fallback internally)
        response_text = await process_message(phone, message_text, contact_name)

        # Classifier metadata for dashboard analytics only
        result = classifier.classify(message_text)
        category = result.get("category", "unknown")
        confidence = result.get("confidence", 0.0)

        # Escalation check
        if category in {"complaint", "return_refund"} or "Connecting to Human Agent" in (response_text or ""):
            session_manager.escalate(phone)
            if "Transferring to live agent" not in (response_text or ""):
                response_text = (
                    f"{response_text}\n\n"
                    "💬 تم تحويلك لممثل خدمة العملاء\n"
                    "Transferring to live agent..."
                )

        # Save to history
        session.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": message_text,
            "assistant": response_text,
            "category": category,
            "confidence": confidence
        })

        # Send reply via bridge (unless test number)
        if response_text and not phone.startswith("97100000"):
            await send_message(phone, response_text)

        # Return reply to bridge
        return {"reply": response_text}

    except Exception as e:
        print(f"Webhook error: {e}")
        return {"reply": None}


# ============================================
# API ENDPOINTS
# ============================================

@whatsapp_router.get("/status")
async def status():
    """Check WhatsApp bridge status"""
    bridge = await get_status()
    return {
        "bridge": bridge,
        "deepseek_configured": bool(__import__('os').getenv("DEEPSEEK_API_KEY"))
    }

@whatsapp_router.get("/send")
async def send_api(
    phone: str = Query(...),
    message: str = Query(...)
):
    """Direct send endpoint"""
    result = await send_message(phone, message)
    return result

@whatsapp_router.get("/chat")
async def chat_api(
    phone: str = Query(...),
    message: str = Query(...),
    name: str = Query(default="Guest")
):
    """Test chat endpoint using menu engine + DeepSeek fallback."""

    session = session_manager.get_session(phone)
    if not session:
        session = session_manager.create_session(phone, name)

    session.last_activity = datetime.now()
    session.message_count += 1

    result = classifier.classify(message)
    category = result.get("category", "unknown")
    confidence = result.get("confidence", 0.0)

    response_text = await process_message(phone, message, name)

    # safe simulation number => no live send
    if phone.startswith("97100000"):
        send_result = {"status": "test_mode_skip_send"}
    else:
        send_result = await send_message(phone, response_text)

    return {
        "sent": send_result.get("status") in {"sent", "test_mode_skip_send"},
        "send_status": send_result.get("status"),
        "response": response_text,
        "category": category,
        "confidence": confidence,
        "mode": "menu_engine_with_ai_fallback"
    }

@whatsapp_router.get("/dashboard")
async def whatsapp_dashboard():
    """Dashboard"""
    stats = session_manager.get_stats()
    training = classifier.get_training_summary()
    bridge = await get_status()
    return {
        "bridge": bridge,
        "sessions": stats,
        "training": training
    }

@whatsapp_router.get("/agent/queue")
async def agent_queue():
    """Escalated sessions"""
    escalated = session_manager.get_escalated_sessions()
    return {
        "total": len(escalated),
        "sessions": [
            {
                "phone": s.phone[-4:],
                "name": s.name,
                "messages": s.message_count,
                "escalated_at": s.escalated_at.isoformat() if s.escalated_at else None
            }
            for s in escalated
        ]
    }

@whatsapp_router.post("/agent/resolve/{phone}")
async def agent_resolve(phone: str):
    """Mark resolved"""
    session = session_manager.get_session(phone)
    if session:
        session.status = "resolved"
        return {"status": "resolved"}
    return {"status": "not_found"}


# ── Training API ──────────────────────────────────────
@whatsapp_router.get("/training/list")
async def training_list():
    """View training examples summary."""
    return training.get_stats()


@whatsapp_router.post("/training/add")
async def training_add(request: Request):
    """Add new training example for classifier."""
    body = await request.json()
    example = training.add_example(
        category=body.get("category", "general"),
        examples=body.get("examples", []),
        response_en=body.get("response_en"),
        response_ar=body.get("response_ar"),
        should_escalate=body.get("should_escalate", False),
        tags=body.get("tags", []),
    )
    return {"status": "added", "example": example}


@whatsapp_router.get("/training/categories")
async def training_categories():
    """Category summary."""
    return training.get_stats().get("categories", {})
