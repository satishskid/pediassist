#!/usr/bin/env python3
"""
Quick Test Script for PediAssist
Tests the local server and provides access information
"""

import subprocess
import requests
import json

def test_local_server():
    """Test local server endpoints"""
    print("🧪 Testing PediAssist Local Server...")
    
    base_url = "http://localhost:8000"
    
    # Test simple interface
    try:
        response = requests.get(f"{base_url}/simple", timeout=5)
        if response.status_code == 200:
            print("✅ Simple interface is working!")
            print(f"   📱 URL: {base_url}/simple")
        else:
            print(f"❌ Simple interface returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Simple interface error: {e}")
    
    # Test main interface
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Main interface is working!")
            print(f"   🏠 URL: {base_url}/")
        else:
            print(f"❌ Main interface returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Main interface error: {e}")
    
    # Test API health
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy!")
        else:
            print(f"⚠️  API returned: {response.status_code}")
    except Exception as e:
        print(f"⚠️  API health check failed: {e}")

def show_access_info():
    """Show access information"""
    print("\n" + "="*50)
    print("🎯 QUICK ACCESS INFORMATION")
    print("="*50)
    print("🌐 Local Server URLs:")
    print("   📱 Simple Interface: http://localhost:8000/simple")
    print("   🏠 Full Interface: http://localhost:8000/")
    print("   🔧 API Base: http://localhost:8000/api")
    print("\n💡 Bookmark the simple interface for quick access!")

if __name__ == "__main__":
    test_local_server()
    show_access_info()
