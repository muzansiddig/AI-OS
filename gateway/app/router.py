from app.services.classifier import classifier
from app.services.dispatcher import dispatcher
from app.services.client import client

class Router:

    async def chat(self, prompt: str):

        service_name = classifier.classify(prompt)

        service = dispatcher.get_service(service_name)

        result = await client.chat(service, prompt)

        return {
            "service": service_name,
            "response": result
        }

router = Router()
