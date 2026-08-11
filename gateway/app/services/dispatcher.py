from app.services.client import client
from app.services.registry import service_registry


class Dispatcher:

    def get_service(self, name: str):
        config = service_registry.get_service(name)
        if not config:
            return None
        return {
            "name": config.name,
            "url": config.url,
            "port": config.port,
            "workspace": config.workspace,
            "capabilities": config.capabilities,
            "description": config.description,
            "enabled": config.enabled,
        }

    def has_service(self, name: str) -> bool:
        return service_registry.has_service(name)

    def list_services(self) -> list[str]:
        return service_registry.list_services()

    async def dispatch(self, service_name: str, payload: dict, timeout: float = 180.0) -> dict:
        config = service_registry.get_service(service_name)
        if not config:
            return {
                "success": False,
                "status_code": 404,
                "error": "service_not_found",
                "message": f"Service '{service_name}' is not registered or enabled.",
            }

        return await client.chat(config.url, payload, timeout=timeout)


dispatcher = Dispatcher()
