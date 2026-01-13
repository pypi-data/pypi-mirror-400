#!/usr/bin/env python
"""
Simple test script for the Bioinformatics Tools API

Usage:
    1. Start the server: dane-api (or python -m bioinformatics_tools.api.main)
    2. Run this script: python test_api.py
"""
import json
from pathlib import Path

import requests

API_BASE_URL = "http://localhost:8000"


def test_health():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{API_BASE_URL}/health", timeout=3)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_root():
    """Test the root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{API_BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_fasta_health():
    """Test the fasta health endpoint"""
    print("\n=== Testing FASTA Health ===")
    response = requests.get(f"{API_BASE_URL}/v1/fasta/health", timeout=3)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_gc_content():
    """Test the GC content endpoint"""
    print("\n=== Testing GC Content Calculation ===")

    # Find the example fasta file
    test_file = Path(__file__).parent.parent / "test-files" / "example.fasta"

    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False

    print(f"Using test file: {test_file}")

    # Test with default precision
    # print("\n--- Test 1: Default precision (2) ---")
    response = requests.post(
        f"{API_BASE_URL}/v1/fasta/gc_content",
        json={
            "file_path": str(test_file),
            "precision": 2
        },
        timeout=3
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    result = response.json()

    # Verify we got data back
    # if response.status_code == 200 and result.get("status") == "success":
    if response.status_code == 200:
        print(f"\n✅ Successfully calculated GC content for {result} sequences")
        return True
    else:
        print("\n❌ Test failed")
        return False


def test_gc_content_total():
    """Test the GC content endpoint"""
    print("\n=== Testing GC Content TOTAL Calculation ===")

    # Find the example fasta file
    test_file = Path(__file__).parent.parent / "test-files" / "example.fasta"

    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False

    print(f"Using test file: {test_file}")

    # Test with default precision
    # print("\n--- Test 1: Default precision (2) ---")
    response = requests.post(
        f"{API_BASE_URL}/v1/fasta/gc_content_total",
        json={
            "file_path": str(test_file),
            "precision": 2
        },
        timeout=3
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    result = response.json()

    # Verify we got data back
    # if response.status_code == 200 and result.get("status") == "success":
    if response.status_code == 200:
        print(f"\n✅ Successfully calculated GC content for {result} sequences")
        return True
    else:
        print("\n❌ Test failed")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Bioinformatics Tools API - Test Suite")
    print("=" * 60)
    print(f"API URL: {API_BASE_URL}")
    print("=" * 60)

    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("FASTA Health", test_fasta_health),
        ("GC Content", test_gc_content),
        ("GC Content Total", test_gc_content_total),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except requests.exceptions.ConnectionError:
            print("\n❌ Connection Error: Is the API server running?")
            print("   Start it with: dane-api")
            return
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")

    passed = sum(1 for _, s in results if s)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    main()
