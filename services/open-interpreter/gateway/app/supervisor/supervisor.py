import httpx
from app.services.classifier import classifier
from app.services.dispatcher import dispatcher

class Supervisor:

    async def execute(self, prompt: str):

        service_name = classifier.classify(prompt)

        service = dispatcher.get_service(service_name)

        async with httpx.AsyncClient(timeout=600) as client:

            response = await client.post(
                f"{service['url']}/chat",
                json={
                    "prompt": prompt
                }
            )

        return response.json()

supervisor = Supervisor()

