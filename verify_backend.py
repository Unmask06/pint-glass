import json
import urllib.request


def test_endpoint(url, data, headers=None):
    if headers is None:
        headers = {}

    headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.load(response)
            return result
    except urllib.error.HTTPError as e:
        print(f"Error: {e.read().decode()}")
        return None


def run_tests():
    print("Running tests...")
    base_url = "http://localhost:8000/items"

    # Test 1: Imperial (Default)
    # Input: 10 (feet) -> Internal: 3.048m -> Output: 10 (feet)
    print("\nTest 1: Imperial (Default)")
    res1 = test_endpoint(base_url, {"length": 10, "name": "test1"})
    print(f"Result: {res1}")
    if res1 and res1["length"] == 10.0:
        print("PASS")
    else:
        print("FAIL")

    # Test 2: SI
    # Input: 10 (meters) -> Internal: 10m -> Output: 10 (meters)
    print("\nTest 2: SI")
    res2 = test_endpoint(
        base_url, {"length": 10, "name": "test2"}, headers={"X-Unit-System": "si"}
    )
    print(f"Result: {res2}")
    if res2 and res2["length"] == 10.0:
        print("PASS")
    else:
        print("FAIL")


if __name__ == "__main__":
    run_tests()
