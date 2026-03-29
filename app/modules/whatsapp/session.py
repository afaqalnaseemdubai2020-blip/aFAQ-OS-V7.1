"""Session Manager — wraps the sessions module for router compatibility."""
from app.modules.whatsapp.sessions import sessions as _sessions
from datetime import datetime

class Session:
    def __init__(self, phone, name="Guest"):
        self.phone = phone
        self.name = name
        self.status = "active"
        self.message_count = 0
        self.template_hits = 0
        self.ai_hits = 0
        self.last_activity = datetime.now()
        self.escalated_at = None
        self.conversation_history = []

class SessionManager:
    def __init__(self):
        self._sessions = {}

    def get_session(self, phone):
        return self._sessions.get(phone)

    def create_session(self, phone, name="Guest"):
        s = Session(phone, name)
        self._sessions[phone] = s
        return s

    def escalate(self, phone):
        s = self._sessions.get(phone)
        if s:
            s.status = "escalated"
            s.escalated_at = datetime.now()
            _sessions.escalate(
                _sessions.get_or_create(phone, s.name)["session_id"],
                "bot_escalation"
            )

    def get_escalated_sessions(self):
        return [s for s in self._sessions.values() if s.status == "escalated"]

    def get_stats(self):
        total = len(self._sessions)
        active = len([s for s in self._sessions.values() if s.status == "active"])
        escalated = len([s for s in self._sessions.values() if s.status == "escalated"])
        return {
            "total": total,
            "active": active,
            "escalated": escalated
        }

session_manager = SessionManager()