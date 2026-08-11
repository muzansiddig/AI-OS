class Planner:
    def plan(self, prompt: str):
        text = prompt.lower()

        plan = []

        if "github" in text:
            plan.append("browser_use")

        if "react" in text or "project" in text:
            plan.append("openhands")

        if "agent" in text or "workflow" in text:
            plan.append("crewai")

        if "افتح" in prompt or "terminal" in text:
            plan.append("open_interpreter")

        if not plan:
            plan.append("open_interpreter")

        return plan

planner = Planner()
