"""Intent Classifier — matches customer messages to training examples."""
from app.modules.whatsapp.training import training

class Classifier:
    def classify(self, message: str) -> dict:
        result = training.get_response(message)
        return {
            "category": result.get("category", "unknown"),
            "confidence": result.get("confidence", 0.0),
            "response": result.get("response"),
            "should_escalate": result.get("should_escalate", False)
        }
    
    def get_training_summary(self) -> dict:
        return training.get_stats()

classifier = Classifier()