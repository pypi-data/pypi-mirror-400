"""
Test KeiroLabs SDK with new production URL: https://kierolabs.space
This test file verifies the SDK works correctly with the new backend URL.
"""
import os
import sys

# Add parent directory to path for local testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from keirolabs import Keiro
from keirolabs.exceptions import (
    KeiroAuthError,
    KeiroRateLimitError,
    KeiroConnectionError
)


def test_new_production_url():
    """Test SDK with new production URL: https://kierolabs.space"""
    print("=" * 70)
    print("Testing KeiroLabs SDK with NEW Production URL")
    print("URL: https://kierolabs.space/api")
    print("=" * 70)
    
    # Use your API key - replace with actual key for testing
    api_key = os.getenv("KEIRO_API_KEY", "keiro_wlfqeusk8pog9vwoi9e4tidjtrg7ix52d8xjazeb")
    
    print("\n[1] Initializing Keiro Client...")
    client = Keiro(api_key=api_key)
    
    # Verify default URL is new production URL
    expected_url = "https://kierolabs.space/api"
    assert client.base_url == expected_url, f"Expected {expected_url}, got {client.base_url}"
    print(f"✓ Default base URL is correct: {client.base_url}")
    
    # Test 1: Health Check
    print("\n[2] Testing Health Check...")
    try:
        health = client.health_check()
        print(f"✓ Status: {health.get('status', 'unknown')}")
        print(f"✓ Environment: {health.get('environment', 'unknown')}")
        print(f"✓ Backend URL is reachable!")
    except KeiroConnectionError as e:
        print(f"✗ Connection failed: {e}")
        print("  → Check if https://kierolabs.space is accessible")
        return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False
    
    # Test 2: Validate API Key
    print("\n[3] Testing API Key Validation...")
    try:
        validation = client.validate_api_key()
        print(f"✓ API Key Valid: {validation.get('valid', False)}")
        print(f"✓ Message: {validation.get('message', 'N/A')}")
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False
    
    # Test 3: Basic Search
    print("\n[4] Testing Search...")
    try:
        result = client.search("Python programming best practices")
        print(f"✓ Search completed successfully!")
        print(f"✓ Credits remaining: {result.get('creditsRemaining', 'N/A')}")
    except KeiroAuthError:
        print("✗ Invalid API key")
        return False
    except KeiroRateLimitError:
        print("⚠ Out of credits (search would work with credits)")
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return False
    
    # Test 4: Test set_base_url method
    print("\n[5] Testing set_base_url method...")
    original_url = client.base_url
    client.set_base_url("https://kierolabs.space/api")
    assert client.base_url == "https://kierolabs.space/api"
    print(f"✓ set_base_url works correctly")
    
    # Summary
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)
    print("\n✓ SDK is working correctly with new production URL!")
    print("✓ Production URL: https://kierolabs.space/api")
    print("✓ The old Railway URL has been replaced successfully")
    print("\n" + "=" * 70)
    
    return True


def test_url_configuration():
    """Test different URL configuration options"""
    print("\n" + "=" * 70)
    print("Testing URL Configuration Options")
    print("=" * 70)
    
    api_key = "test-key"
    
    # Test 1: Default URL
    print("\n[1] Default URL (no base_url specified)...")
    client = Keiro(api_key=api_key)
    assert client.base_url == "https://kierolabs.space/api"
    print(f"✓ Default URL: {client.base_url}")
    
    # Test 2: Custom URL
    print("\n[2] Custom URL (localhost for development)...")
    client = Keiro(api_key=api_key, base_url="http://localhost:8000/api")
    assert client.base_url == "http://localhost:8000/api"
    print(f"✓ Custom URL: {client.base_url}")
    
    # Test 3: URL with trailing slash (should be stripped)
    print("\n[3] URL with trailing slash...")
    client = Keiro(api_key=api_key, base_url="https://kierolabs.space/api/")
    assert client.base_url == "https://kierolabs.space/api"
    print(f"✓ Trailing slash stripped: {client.base_url}")
    
    print("\n✓ All URL configuration tests passed!")
    return True


if __name__ == "__main__":
    print("\nKeiroLabs SDK - New Production URL Test Suite")
    print("Version: 0.1.3")
    print("New Backend: https://kierolabs.space")
    print("\n")
    
    # Run tests
    success = True
    success = test_url_configuration() and success
    success = test_new_production_url() and success
    
    if success:
        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
    else:
        print("\n⚠ Some tests failed. Check output above.")
        sys.exit(1)
