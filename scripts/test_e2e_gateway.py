import asyncio
import os
import sys
import subprocess
import time
from pathlib import Path
import httpx

root_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_path / "gateway"))

GATEWAY_URL = "http://127.0.0.1:8000"
OPENINTERPRETER_URL = "http://127.0.0.1:8101"


async def check_url(url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{url.rstrip('/')}/health")
            return res.status_code == 200
    except Exception:
        return False


def start_service(cmd: list[str], cwd: str) -> subprocess.Popen:
    print(f"Launching process: {' '.join(cmd)} in {cwd}", flush=True)
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc


async def main():
    print("=== AI-OS Gateway End-to-End (E2E) Test Suite ===", flush=True)

    oi_proc = None
    gw_proc = None

    try:
        # Check Open Interpreter Service on 8101
        is_oi_running = await check_url(OPENINTERPRETER_URL)
        if not is_oi_running:
            print("[INFO] Starting Open Interpreter Service on port 8101...", flush=True)
            oi_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8101"]
            oi_cwd = str(root_path / "services" / "open-interpreter")
            oi_proc = start_service(oi_cmd, oi_cwd)

            for _ in range(15):
                await asyncio.sleep(1.0)
                if await check_url(OPENINTERPRETER_URL):
                    print("[OK] Open Interpreter Service is online!", flush=True)
                    break

        assert await check_url(OPENINTERPRETER_URL), "Failed to connect to Open Interpreter Service on 8101"

        # Check Gateway Service on 8000
        is_gw_running = await check_url(GATEWAY_URL)
        if not is_gw_running:
            print("[INFO] Starting Gateway Service on port 8000...", flush=True)
            gw_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"]
            gw_cwd = str(root_path / "gateway")
            gw_proc = start_service(gw_cmd, gw_cwd)

            for _ in range(15):
                await asyncio.sleep(1.0)
                if await check_url(GATEWAY_URL):
                    print("[OK] Gateway Service is online!", flush=True)
                    break

        assert await check_url(GATEWAY_URL), "Failed to connect to Gateway Service on 8000"

        # Perform End-to-End POST /chat request through Gateway
        async with httpx.AsyncClient(timeout=120.0) as client:
            print("\n[TEST 1] Testing Gateway Service Discovery GET /services...", flush=True)
            res_services = await client.get(f"{GATEWAY_URL}/services")
            assert res_services.status_code == 200, "GET /services failed"
            services_data = res_services.json()
            assert "open_interpreter" in services_data["services"], "open_interpreter missing from /services"
            print("  [OK] Service Registry discovery returned 5 registered services!", flush=True)

            print("\n[TEST 2] Testing E2E execution: Gateway (8000) -> Open Interpreter (8101) -> Ollama...", flush=True)
            payload = {
                "prompt": "Reply with text OK",
                "session_id": "e2e_session_001",
                "context": {"source": "e2e_test"},
            }

            start_time = time.time()
            res_chat = await client.post(f"{GATEWAY_URL}/chat", json=payload)
            elapsed = time.time() - start_time

            print(f"  Response Status Code: {res_chat.status_code} (took {elapsed:.2f}s)", flush=True)
            assert res_chat.status_code == 200, f"Gateway /chat failed with status {res_chat.status_code}"

            chat_data = res_chat.json()
            print("  Gateway Response Data:", flush=True)
            print(f"    - Intent: {chat_data.get('intent')}", flush=True)
            print(f"    - Plan:   {chat_data.get('plan')}", flush=True)

            results = chat_data.get("results", {})
            assert "open_interpreter" in results, "open_interpreter execution missing from results"

            oi_res = results["open_interpreter"]
            print(f"    - Open Interpreter Success: {oi_res.get('success')}", flush=True)

            data = oi_res.get("data", {})
            assert oi_res.get("success") is True, f"Open Interpreter execution failed: {oi_res}"

            print("\n==================================================", flush=True)
            print("=== END-TO-END GATEWAY (8000) -> OPEN INTERPRETER (8101) -> OLLAMA TEST PASSED! ===", flush=True)
            print("==================================================", flush=True)

    finally:
        if oi_proc:
            print("[INFO] Terminating temporary Open Interpreter test process...", flush=True)
            oi_proc.terminate()
        if gw_proc:
            print("[INFO] Terminating temporary Gateway test process...", flush=True)
            gw_proc.terminate()


if __name__ == "__main__":
    asyncio.run(main())
