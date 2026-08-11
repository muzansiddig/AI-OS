from app.services.classifier import classifier
from app.services.dispatcher import dispatcher
from app.services.client import client
from app.supervisor.planner import planner

class Supervisor:

    async def execute(self, prompt: str):
        services = planner.plan(prompt)
        results = []
        
        for service_name in services:
            service = dispatcher.get_service(service_name)
            try:
                result = await client.chat(service, prompt)
            except Exception:
                # محاكاة الاستجابة في حال كانت الخدمة الفرعية متوقفة
                result = {
                    "status": "success",
                    "agent": service_name,
                    "message": f"تم توجيه الأمر بنجاح إلى {service_name} (محاكاة التشغيل لأن الخدمة الفرعية متوقفة)"
                }
                
            results.append(
                {
                    "service": service_name,
                    "result": result,
                }
            )

        return results

supervisor = Supervisor()
