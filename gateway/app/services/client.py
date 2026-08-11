import httpx


class Client:

    async def check_health(self, service_url: str, timeout: float = 3.0) -> dict:
        if not service_url.startswith(("http://", "https://")):
            service_url = f"http://{service_url}"

        url = f"{service_url.rstrip('/')}/health"

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    try:
                        return {"healthy": True, "data": response.json(), "url": url}
                    except Exception:
                        return {"healthy": True, "data": {"raw": response.text}, "url": url}
                return {
                    "healthy": False,
                    "error": f"http_{response.status_code}",
                    "message": f"Service returned HTTP status {response.status_code}",
                    "url": url,
                }
        except httpx.ConnectError as e:
            return {
                "healthy": False,
                "error": "service_unavailable",
                "message": f"Connection failed: {e}",
                "url": url,
            }
        except httpx.TimeoutException as e:
            return {
                "healthy": False,
                "error": "timeout",
                "message": f"Health check timed out: {e}",
                "url": url,
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": "client_error",
                "message": str(e),
                "url": url,
            }

    async def chat(self, service: str, payload: dict, timeout: float = 180.0) -> dict:
        if not service.startswith(("http://", "https://")):
            service = f"http://{service}"

        url = f"{service.rstrip('/')}/chat"

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                try:
                    data = response.json()
                except Exception:
                    data = {"raw": response.text}

                return {
                    "status_code": response.status_code,
                    "success": response.is_success,
                    "data": data,
                }

        except httpx.ConnectError as e:
            return {
                "success": False,
                "status_code": 503,
                "error": "service_unavailable",
                "message": f"Cannot connect to agent service at {url}: {e}",
                "url": url,
            }

        except httpx.TimeoutException as e:
            return {
                "success": False,
                "status_code": 504,
                "error": "timeout",
                "message": f"Request to agent service timed out at {url}: {e}",
                "url": url,
            }

        except Exception as e:
            return {
                "success": False,
                "status_code": 500,
                "error": "client_error",
                "message": str(e),
                "url": url,
            }


client = Client()
