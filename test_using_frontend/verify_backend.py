"""Verification script for PintGlass Demo Backend.

Tests the /pump and /line endpoints with different unit systems.
"""

import json
import urllib.request


def test_endpoint(url: str, data: dict, unit_system: str = "imperial") -> dict | None:
    """Send POST request and return response."""
    headers = {
        "Content-Type": "application/json",
        "X-Unit-System": unit_system,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        print(f"  ERROR: {e.read().decode()}")
        return None
    except urllib.error.URLError as e:
        print(f"  ERROR: {e.reason}")
        return None


def run_tests():
    """Run all verification tests."""
    base_url = "http://localhost:8001"

    print("=" * 60)
    print("PintGlass Demo Backend Verification")
    print("=" * 60)

    # Test 1: Health check
    print("\n[Test 1] Health Check")
    try:
        with urllib.request.urlopen(f"{base_url}/health") as resp:
            health = json.load(resp)
            if health.get("status") == "ok":
                print("  ✅ PASS - Backend is running")
            else:
                print("  ❌ FAIL - Unexpected response")
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
        print(
            "\n  --> Is the backend running? Start with: uv run python fast_api_check.py"
        )
        return

    # Test 2: Pump endpoint with Imperial
    print("\n[Test 2] Pump Endpoint - Imperial")
    pump_data = {
        "flow_rate": 100,
        "head_pressure": 50,
        "power": 10,
        "inlet_temperature": 68,
        "pipe_diameter": 4,
    }
    result = test_endpoint(f"{base_url}/pump", pump_data, "imperial")
    if result and abs(result["data"]["flow_rate"] - 100) < 0.001:
        print("  ✅ PASS - Round-trip conversion correct")
        print(
            f"     Input: 100 ft³/s → Output: {result['data']['flow_rate']:.4f} ft³/s"
        )
    else:
        print("  ❌ FAIL")

    # Test 3: Pump endpoint with SI
    print("\n[Test 3] Pump Endpoint - SI")
    result = test_endpoint(f"{base_url}/pump", pump_data, "si")
    if result and abs(result["data"]["flow_rate"] - 100) < 0.001:
        print("  ✅ PASS - Round-trip conversion correct")
        print(f"     Input: 100 m³/s → Output: {result['data']['flow_rate']:.4f} m³/s")
    else:
        print("  ❌ FAIL")

    # Test 4: Line endpoint with Imperial
    print("\n[Test 4] Line Endpoint - Imperial")
    line_data = {
        "length": 1000,
        "velocity": 10,
        "pressure_drop": 15,
        "fluid_density": 62.4,
        "viscosity": 0.001,
    }
    result = test_endpoint(f"{base_url}/line", line_data, "imperial")
    if result and abs(result["data"]["length"] - 1000) < 0.001:
        print("  ✅ PASS - Round-trip conversion correct")
        print(f"     Input: 1000 ft → Output: {result['data']['length']:.4f} ft")
    else:
        print("  ❌ FAIL")

    # Test 5: Line endpoint with SI
    print("\n[Test 5] Line Endpoint - SI")
    result = test_endpoint(f"{base_url}/line", line_data, "si")
    if result and abs(result["data"]["length"] - 1000) < 0.001:
        print("  ✅ PASS - Round-trip conversion correct")
        print(f"     Input: 1000 m → Output: {result['data']['length']:.4f} m")
    else:
        print("  ❌ FAIL")

    # Test 6: Dimensions endpoint
    print("\n[Test 6] Dimensions Endpoint")
    try:
        with urllib.request.urlopen(f"{base_url}/dimensions") as resp:
            dims = json.load(resp)
            if "dimensions" in dims and len(dims["dimensions"]) > 0:
                print(f"  ✅ PASS - {len(dims['dimensions'])} dimensions available")
                print(f"     Sample: {dims['dimensions'][:5]}...")
            else:
                print("  ❌ FAIL")
    except Exception as e:
        print(f"  ❌ FAIL - {e}")

    print("\n" + "=" * 60)
    print("Verification complete!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
