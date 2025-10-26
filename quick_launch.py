#!/usr/bin/env python3
"""
Quick Launch Script for PediAssist
Opens the application in your default browser
"""

import webbrowser
import requests
import time
import sys

def check_and_launch():
    """Check if server is running and launch browser"""
    
    print("🚀 PediAssist Quick Launch")
    print("="*30)
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:8000/simple", timeout=3)
        if response.status_code == 200:
            print("✅ Server is running!")
            print("🌐 Opening in browser...")
            
            # Open both interfaces
            webbrowser.open('http://localhost:8000/simple')
            time.sleep(1)
            webbrowser.open('http://localhost:8000/')
            
            print("📱 Simple interface: http://localhost:8000/simple")
            print("🏠 Full interface: http://localhost:8000/")
            print("✅ Done! Check your browser.")
            return True
        else:
            print(f"❌ Server returned error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        print("💡 Start it with: python -m pediassist.web_app")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    success = check_and_launch()
    
    if not success:
        print("\\n🔧 Quick Fix Options:")
        print("1. Start server: python -m pediassist.web_app")
        print("2. Check status: ./server_manager.sh status")
        print("3. Run tests: ./test_access.py")
        sys.exit(1)
    else:
        print("\\n💡 Bookmark http://localhost:8000/simple for quick access!")

if __name__ == "__main__":
    main()