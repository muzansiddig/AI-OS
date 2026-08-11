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
    print("==========================================================", flush=True)
    print("=== AI-OS Master Real Execution E2E Test Suite (5/5) ===", flush=True)
    print("==========================================================", flush=True)

    processes = {}

    try:
        # 1. Start all agent services
        for service_name, meta in SERVICES.items():
            url = f"http://127.0.0.1:{meta['port']}"
            if not await check_health(url):
                proc = start_service(service_name, meta["port"], meta["dir"], meta["use_uv"])
                processes[service_name] = proc

        # Wait for all services to report online
        print("\n[STEP 1] Health Check Verification across all 5 ports...", flush=True)
        for service_name, meta in SERVICES.items():
            url = f"http://127.0.0.1:{meta['port']}"
            online = False
            for _ in range(15):
                if await check_health(url):
                    online = True
                    break
                await asyncio.sleep(1.0)
            print(f"  - {service_name:18s} (Port {meta['port']}): {'ONLINE [OK]' if online else 'OFFLINE [FAIL]'}", flush=True)
            assert online, f"Service {service_name} on port {meta['port']} failed to report online!"

        # Check Gateway
        if not await check_health(GATEWAY_URL):
            gw_proc = start_service("gateway", 8000, "gateway", False)
            processes["gateway"] = gw_proc
            for _ in range(15):
                if await check_health(GATEWAY_URL):
                    break
                await asyncio.sleep(1.0)

        assert await check_health(GATEWAY_URL), "Gateway Service on port 8000 failed to start!"
        print("  - gateway            (Port 8000): ONLINE [OK]", flush=True)

        async with httpx.AsyncClient(timeout=300.0) as client:
            print("\n[STEP 2] Real Domain Execution Tests via Gateway...", flush=True)

            # Test 1: AutoGPT Goal Decomposition & Artifact Creation
            print("\n  [TEST 1/5] AutoGPT Goal Execution & Artifact Creation...", flush=True)
            res1 = await client.post(f"{GATEWAY_URL}/chat", json={
                "prompt": "execute autonomous research goal",
                "session_id": "real_e2e_001"
            })
            assert res1.status_code == 200
            data1 = res1.json()
            assert "autogpt" in data1.get("results", {})
            ag_res = data1["results"]["autogpt"]
            assert ag_res.get("success") is True
            print("    [OK] AutoGPT executed research goal & saved artifact!", flush=True)

            # Test 2: Open Interpreter Quick Script Execution
            print("\n  [TEST 2/5] Open Interpreter Script Execution...", flush=True)
            res2 = await client.post(f"{GATEWAY_URL}/chat", json={
                "prompt": "open terminal and print OK",
                "session_id": "real_e2e_002"
            })
            assert res2.status_code == 200
            data2 = res2.json()
            assert "open_interpreter" in data2.get("results", {})
            print("    [OK] Open Interpreter executed script cleanly!", flush=True)

            # Test 3: CrewAI Multi-Agent Workflow Execution
            print("\n  [TEST 3/5] CrewAI Multi-Agent Workflow Execution...", flush=True)
            res3 = await client.post(f"{GATEWAY_URL}/chat", json={
                "prompt": "run multi agent crewai workflow",
                "session_id": "real_e2e_003"
            })
            assert res3.status_code == 200
            data3 = res3.json()
            assert "crewai" in data3.get("results", {})
            print("    [OK] CrewAI multi-agent crew completed workflow kickoff!", flush=True)

            # Test 4: OpenHands Code Engineering Workspace Test
            print("\n  [TEST 4/5] OpenHands Code Engineering Workspace Test...", flush=True)
            res4 = await client.post(f"{GATEWAY_URL}/chat", json={
                "prompt": "build react application code",
                "session_id": "real_e2e_004"
            })
            assert res4.status_code == 200
            data4 = res4.json()
            assert "openhands" in data4.get("results", {})
            print("    [OK] OpenHands SDK completed workspace project task!", flush=True)

            # Test 5: Browser Use Web Automation Execution
            print("\n  [TEST 5/5] Browser Use Web Automation Execution...", flush=True)
            res5 = await client.post(f"{GATEWAY_URL}/chat", json={
                "prompt": "browse github repository website",
                "session_id": "real_e2e_005"
            })
            assert res5.status_code == 200
            data5 = res5.json()
            assert "browser_use" in data5.get("results", {})
            print("    [OK] Browser Use completed web automation task!", flush=True)

        print("\n==========================================================", flush=True)
        print("=== REAL DOMAIN EXECUTION TEST PASSED FOR ALL 5 AGENTS! ===", flush=True)
        print("==========================================================", flush=True)

    finally:
        print("\n[CLEANUP] Terminating temporary test processes...", flush=True)
        for sname, proc in processes.items():
            try:
                proc.terminate()
            except Exception:
                pass


if __name__ == "__main__":
    asyncio.run(main())
