class Planner:

    def plan(self, prompt: str):

        text = prompt.lower()

        plan = []

        if "github" in text:
            plan.append("browser_use")

        if "react" in text or "project" in text:
            plan.append("openhands")

        if "terminal" in text or "افتح" in prompt:
            plan.append("open_interpreter")

        if "agent" in text or "workflow" in text:
            plan.append("crewai")

        if not plan:
            plan.append("open_interpreter")

        return plan

planner = Planner()
