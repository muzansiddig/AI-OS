from app.supervisor.planner import planner
from app.adapter import adapter

class Supervisor:

    async def execute(self, prompt: str):

        plan = planner.plan(prompt)

        results = []

        for step in plan:

            if step == "browser_use":
                results.append(adapter.chat(prompt))

            else:
                results.append(
                    {
                        "service": step,
                        "status": "delegated"
                    }
                )

        return {
            "plan": plan,
            "results": results
        }

supervisor = Supervisor()

