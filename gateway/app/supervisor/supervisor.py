from typing import Any
from app.artifacts.manager import artifacts
from app.memory.session import memory
from app.services.dispatcher import dispatcher
from app.supervisor.context import context
from app.supervisor.planner import planner


class Supervisor:

    async def execute(
        self,
        prompt: str,
        session_id: str | None = None,
        request_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        request_context = request_context or {}

        memory.add(
            "user",
            {
                "prompt": prompt,
                "session_id": session_id,
                "context": request_context,
            },
        )

        plan_data = planner.plan(prompt)
        intent = plan_data.get("intent", "general_task")
        services = plan_data.get("services", ["open_interpreter"])

        context.set("prompt", prompt)
        context.set("session_id", session_id)
        context.set("intent", intent)
        context.set("request_context", request_context)
        context.set("plan", services)

        results: dict[str, Any] = {}
        for service_name in services:
            service_config = dispatcher.get_service(service_name)
            if not service_config:
                results[service_name] = {
                    "success": False,
                    "error": "service_not_registered",
                    "message": f"Service '{service_name}' is not registered or enabled.",
                }
                continue

            payload = {
                "prompt": prompt,
                "session_id": session_id,
                "context": context.data,
                "artifacts": artifacts.all(),
                "workspace": service_config["workspace"],
                "previous_results": results,
            }

            print()
            print("=" * 60)
            print(f"EXECUTING INTENT: {intent} -> SERVICE: {service_name}")
            print(f"URL: {service_config['url']}")
            print(f"WORKSPACE: {service_config['workspace']}")
            print("=" * 60)

            result = await dispatcher.dispatch(service_name, payload)
            results[service_name] = result
            context.set(service_name, result)

        final_result = {
            "prompt": prompt,
            "intent": intent,
            "plan": services,
            "results": results,
            "context": context.data,
            "artifacts": artifacts.all(),
        }

        memory.add(
            "assistant",
            final_result,
        )

        return final_result


supervisor = Supervisor()
