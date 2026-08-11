import os
import sys
from pathlib import Path

# Add workspace paths
root_path = Path(__file__).resolve().parents[1]
gateway_path = root_path / "gateway"
sys.path.insert(0, str(gateway_path))

from dotenv import load_dotenv
load_dotenv(dotenv_path=root_path / ".env")

def test_config():
    print("=== 1. Checking Centralized Environment Setup ===")
    ollama_url = os.getenv("OLLAMA_BASE_URL")
    default_model = os.getenv("DEFAULT_MODEL")
    openhands_model = os.getenv("OPENHANDS_MODEL")
    interpreter_model = os.getenv("OPENINTERPRETER_MODEL")
    
    print(f"OLLAMA_BASE_URL: {ollama_url}")
    print(f"DEFAULT_MODEL: {default_model}")
    print(f"OPENHANDS_MODEL: {openhands_model}")
    print(f"OPENINTERPRETER_MODEL: {interpreter_model}")
    
    assert ollama_url is not None, "OLLAMA_BASE_URL should be set in .env"
    assert default_model is not None, "DEFAULT_MODEL should be set in .env"
    print("[OK] Environment configuration passed!")

def test_registry():
    print("\n=== 2. Checking Gateway Service Registry & Ports ===")
    from app.services.registry import service_registry
    
    expected_ports = {
        "open_interpreter": 8101,
        "browser_use": 8102,
        "openhands": 8103,
        "crewai": 8104,
        "autogpt": 8105,
    }
    
    for service_name, expected_port in expected_ports.items():
        config = service_registry.get_service(service_name)
        assert config is not None, f"Service '{service_name}' missing from registry"
        assert config.port == expected_port, f"Port mismatch for {service_name}: expected {expected_port}, got {config.port}"
        print(f"  - {service_name:18s} -> Port {config.port} ({config.url}) | Capabilities: {len(config.capabilities)}")
        
    print("[OK] Service Registry & Port allocation passed!")

def test_planner():
    print("\n=== 3. Checking Capability Router & Planner ===")
    from app.supervisor.planner import planner
    
    test_cases = [
        ("open folder and create python file", ["open_interpreter"]),
        ("search github for react project", ["browser_use", "openhands"]),
        ("build a react app and fix errors", ["openhands"]),
        ("run crewai workflow with multiple agents", ["crewai"]),
    ]
    
    for prompt, expected_services in test_cases:
        plan = planner.plan(prompt)
        print(f"  Prompt: '{prompt}'")
        print(f"  Plan:   {plan}")
        assert any(s in plan for s in expected_services), f"Plan {plan} did not include expected services {expected_services}"
        
    print("[OK] Capability Router & Planner passed!")

def test_contract_schemas():
    print("\n=== 4. Checking Unified Service Contract Schemas ===")
    from app.schemas.contract import AgentChatRequest, AgentChatResponse, HealthCheckResponse
    
    req = AgentChatRequest(prompt="Test Prompt", session_id="sess_123")
    res = AgentChatResponse(success=True, service="openhands", result="OK")
    health = HealthCheckResponse(status="healthy", service="openhands", model="ollama/qwen3:8b")
    
    assert req.prompt == "Test Prompt"
    assert res.success is True
    assert health.status == "healthy"
    print("[OK] Contract Schemas passed!")

if __name__ == "__main__":
    test_config()
    test_registry()
    test_planner()
    test_contract_schemas()
    print("\n=== ALL ARCHITECTURAL CHECKS PASSED SUCCESSFULLY! ===")
