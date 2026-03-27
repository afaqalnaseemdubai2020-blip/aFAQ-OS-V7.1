"""
Domain event definitions — backbone of inter-module communication.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum
import uuid


class EventPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BaseEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    source_module: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None


@dataclass
class LeadCreatedEvent(BaseEvent):
    event_type: str = "lead.created"
    source_module: str = "crm"


@dataclass
class InventoryAlertEvent(BaseEvent):
    event_type: str = "inventory.alert"
    source_module: str = "inventory"


@dataclass
class PriceChangeDetectedEvent(BaseEvent):
    event_type: str = "pricing.change_detected"
    source_module: str = "pricing"
    priority: EventPriority = EventPriority.HIGH


@dataclass
class ProductTrendDetectedEvent(BaseEvent):
    event_type: str = "market_intelligence.trend_detected"
    source_module: str = "market_intelligence"


@dataclass
class TaskOverdueEvent(BaseEvent):
    event_type: str = "scheduling.task_overdue"
    source_module: str = "scheduling"
    priority: EventPriority = EventPriority.HIGH


@dataclass
class ReportGeneratedEvent(BaseEvent):
    event_type: str = "reporting.generated"
    source_module: str = "reporting"


@dataclass
class EmployeeCheckInEvent(BaseEvent):
    event_type: str = "employee.check_in"
    source_module: str = "employee"


@dataclass
class TacticalDelayAlertEvent(BaseEvent):
    event_type: str = "employee.tactical_delay"
    source_module: str = "employee"
    priority: EventPriority = EventPriority.HIGH


@dataclass
class AutomationSuggestionEvent(BaseEvent):
    event_type: str = "automation.suggestion"
    source_module: str = "automation"
    priority: EventPriority = EventPriority.HIGH


@dataclass
class ShopifySyncCompletedEvent(BaseEvent):
    event_type: str = "shopify.sync_completed"
    source_module: str = "shopify"


EVENT_REGISTRY: Dict[str, type] = {
    "lead.created": LeadCreatedEvent,
    "inventory.alert": InventoryAlertEvent,
    "pricing.change_detected": PriceChangeDetectedEvent,
    "market_intelligence.trend_detected": ProductTrendDetectedEvent,
    "scheduling.task_overdue": TaskOverdueEvent,
    "reporting.generated": ReportGeneratedEvent,
    "employee.check_in": EmployeeCheckInEvent,
    "employee.tactical_delay": TacticalDelayAlertEvent,
    "automation.suggestion": AutomationSuggestionEvent,
    "shopify.sync_completed": ShopifySyncCompletedEvent,
}