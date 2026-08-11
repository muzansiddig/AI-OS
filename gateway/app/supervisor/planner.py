from app.services.registry import service_registry
from app.supervisor.classifier import classifier


class Planner:

    def plan(self, prompt: str) -> dict:
        intent_result = classifier.classify(prompt)

        plan = []
        for service_name in intent_result.suggested_services:
            if service_registry.has_service(service_name):
                plan.append(service_name)

        # Fallback to capability matching if classifier suggestion is empty
        if not plan:
            capability_matches = service_registry.match_capabilities(prompt)
            for service_name in capability_matches:
                if service_name not in plan and service_registry.has_service(service_name):
                    plan.append(service_name)

        # Default fallback
        if not plan:
            plan.append("open_interpreter")

        return {
            "intent": intent_result.intent,
            "confidence": intent_result.confidence,
            "services": plan,
        }


planner = Planner()
