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

SERVICES = {
    "open_interpreter": {"port": 8101, "dir": "services/open-interpreter", "use_uv": False},
    "browser_use": {"port": 8102, "dir": "services/browser-use", "use_uv": False},
    "openhands": {"port": 8103, "dir": "services/openhands", "use_uv": True},
    "crewai": {"port": 8104, "dir": "services/crewai", "use_uv": False},
    "autogpt": {"port": 8105, "dir": "services/autogpt", "use_uv": False},
}


async def check_health(service_url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.get(f"{service_url.rstrip('/')}/health")
            return res.status_code == 200
    except Exception:
        return False


def start_service(service_name: str, port: int, service_dir: str, use_uv: bool) -> subprocess.Popen:
    cwd = str(root_path / service_dir)
    if use_uv:
        cmd = ["uv", "run", "python", "-m", "uvicorn", "app.main:app", "--port", str(port)]
    else:
        cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(port)]

    print(f"[INFO] Launching {service_name} on port {port}...", flush=True)
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc


async def main():
    print("==================================================", flush=True)
    print("=== AI-OS Master 5-Service Verification Suite ===", flush=True)
    print("==================================================", flush=True)

    processes = {}

    try:
        # 1. Start all missing agent services
        for service_name, meta in SERVICES.items():
            url = f"http://127.0.0.1:{meta['port']}"
            if not await check_health(url):
                proc = start_service(service_name, meta["port"], meta["dir"], meta["use_uv"])
                processes[service_name] = proc

        # Wait for all services to come online
        print("\n[STEP 1] Waiting for all 5 Agent Services to report HEALTHY...", flush=True)
        for service_name, meta in SERVICES.items():
            url = f"http://127.0.0.1:{meta['port']}"
            online = False
            for _ in range(15):
                if await check_health(url):
                    online = True
                    break
                await asyncio.sleep(1.0)

            status_str = "ONLINE [OK]" if online else "OFFLINE [FAIL]"
            print(f"  - {service_name:18s} (Port {meta['port']}): {status_str}", flush=True)
            assert online, f"Service {service_name} on port {meta['port']} failed to start!"

        # 2. Check Gateway Service
        if not await check_health(GATEWAY_URL):
            gw_proc = start_service("gateway", 8000, "gateway", False)
            processes["gateway"] = gw_proc
            for _ in range(15):
                if await check_health(GATEWAY_URL):
                    break
                await asyncio.sleep(1.0)

        assert await check_health(GATEWAY_URL), "Gateway Service on port 8000 failed to start!"
        print("  - gateway            (Port 8000): ONLINE [OK]", flush=True)

        # 3. Test Gateway Service Discovery & Health API
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("\n[STEP 2] Testing Gateway Service Discovery GET /services...", flush=True)
            res_services = await client.get(f"{GATEWAY_URL}/services")
            assert res_services.status_code == 200
            data_services = res_services.json()
            reg_count = len(data_services.get("services", {}))
            print(f"  [OK] Service Registry returned {reg_count} active services!", flush=True)
            assert reg_count == 5, "Expected 5 registered services in registry!"

            print("\n[STEP 3] Testing Gateway Aggregated Health GET /services/health...", flush=True)
            res_health = await client.get(f"{GATEWAY_URL}/services/health")
            assert res_health.status_code == 200
            health_map = res_health.json().get("services_health", {})
            for sname, sinfo in health_map.items():
                is_healthy = sinfo.get("healthy", False)
                print(f"  - Service {sname:18s} Health Check: {'PASSED [OK]' if is_healthy else 'FAILED [FAIL]'}", flush=True)
                assert is_healthy, f"Health check failed for {sname}"

            print("\n[STEP 4] Testing Gateway Intent Classifier & Planner Pipeline...", flush=True)
            from app.supervisor.planner import planner
            test_prompts = [
                ("open terminal and run command", "terminal_command", "open_interpreter"),
                ("browse github repository website", "web_browsing", "browser_use"),
                ("build react application code", "code_generation", "openhands"),
                ("run multi agent crewai workflow", "multi_agent_workflow", "crewai"),
                ("execute autonomous research goal", "general_task", "autogpt"),
            ]

            for prompt, expected_intent, expected_service in test_prompts:
                plan_result = planner.plan(prompt)
                intent = plan_result.get("intent")
                plan = plan_result.get("services", [])
                print(f"  Prompt: '{prompt}' -> Intent: {intent:20s} | Services: {plan}", flush=True)
                assert expected_service in plan, f"Expected {expected_service} in plan {plan}"
            print("  [OK] Intent Classifier & Planner pipeline validated across all 5 services!", flush=True)

        print("\n==================================================", flush=True)
        print("=== ALL 5 AGENT SERVICES & GATEWAY PASSED MASTER TEST! ===", flush=True)
        print("==================================================", flush=True)

    finally:
        print("\n[CLEANUP] Terminating temporary test processes...", flush=True)
        for sname, proc in processes.items():
            try:
                proc.terminate()
            except Exception:
                pass


if __name__ == "__main__":
    asyncio.run(main())
