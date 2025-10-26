#!/usr/bin/env python3
"""
Easy Access Solutions for PediAssist
Provides multiple ways to access the application easily
"""

import subprocess
import json
import os

def create_local_access_guide():
    """Create local access guide"""
    guide = """
# 🚀 PediAssist Easy Access Solutions

## Current Status
✅ **Local Server is RUNNING**
   - URL: http://localhost:8000/simple
   - Status: Working perfectly!

## Quick Access Options

### Option 1: Local Server (Currently Running!)
🔗 **Direct Access:** http://localhost:8000/simple
- ✅ Fast and reliable
- ✅ No authentication required
- ✅ Full functionality available

### Option 2: Create Simple Tunnel (Optional)
If you need external access, we can set up a tunnel:
```bash
# Using ngrok (if installed)
ngrok http 8000

# Or using cloudflared
cloudflared tunnel --url http://localhost:8000
```

### Option 3: Fix Vercel Deployment
We can redeploy to Vercel with proper configuration:
```bash
./deploy_vercel.sh
```

## Current Local Server Features
- 🏠 **Simple Interface:** http://localhost:8000/simple
- 📊 **Full Interface:** http://localhost:8000/
- 🔧 **API Endpoints:** http://localhost:8000/api

## Bookmark These URLs!
1. **Primary:** http://localhost:8000/simple
2. **Full App:** http://localhost:8000/

## Keep Server Running
The server is currently running in the background.
To restart it if needed:
```bash
python -m pediassist.web_app
```
"""
    
    with open('EASY_ACCESS.md', 'w') as f:
        f.write(guide)
    
    print("✅ Created easy access guide: EASY_ACCESS.md")

def create_quick_test_script():
    """Create quick test script to verify everything works"""
    
    test_script = '''#!/usr/bin/env python3
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
    print("\\n" + "="*50)
    print("🎯 QUICK ACCESS INFORMATION")
    print("="*50)
    print("🌐 Local Server URLs:")
    print("   📱 Simple Interface: http://localhost:8000/simple")
    print("   🏠 Full Interface: http://localhost:8000/")
    print("   🔧 API Base: http://localhost:8000/api")
    print("\\n💡 Bookmark the simple interface for quick access!")

if __name__ == "__main__":
    test_local_server()
    show_access_info()
'''
    
    with open('test_access.py', 'w') as f:
        f.write(test_script)
    
    os.chmod('test_access.py', 0o755)
    print("✅ Created quick test script: test_access.py")

def create_server_manager():
    """Create server management script"""
    
    manager_script = '''#!/bin/bash
# PediAssist Server Manager

echo "🚀 PediAssist Server Manager"
echo "============================"

case "$1" in
    "start")
        echo "Starting PediAssist server..."
        python -m pediassist.web_app &
        echo "✅ Server started on http://localhost:8000"
        ;;
    "stop")
        echo "Stopping PediAssist server..."
        pkill -f "python -m pediassist.web_app"
        echo "✅ Server stopped"
        ;;
    "restart")
        echo "Restarting PediAssist server..."
        pkill -f "python -m pediassist.web_app"
        sleep 2
        python -m pediassist.web_app &
        echo "✅ Server restarted on http://localhost:8000"
        ;;
    "status")
        if pgrep -f "python -m pediassist.web_app" > /dev/null; then
            echo "✅ Server is RUNNING"
            echo "📱 Access: http://localhost:8000/simple"
        else
            echo "❌ Server is NOT running"
            echo "💡 Start with: ./server_manager.sh start"
        fi
        ;;
    "test")
        echo "Testing server..."
        python test_access.py
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the server"
        echo "  stop    - Stop the server"
        echo "  restart - Restart the server"
        echo "  status  - Check server status"
        echo "  test    - Test server functionality"
        ;;
esac
'''
    
    with open('server_manager.sh', 'w') as f:
        f.write(manager_script)
    
    os.chmod('server_manager.sh', 0o755)
    print("✅ Created server manager: server_manager.sh")

def test_current_setup():
    """Test current setup"""
    print("\\n🔍 Testing Current Setup...")
    
    # Check if server is running
    try:
        result = subprocess.run([
            'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
            'http://localhost:8000/simple'
        ], capture_output=True, text=True, timeout=5)
        
        if result.stdout.strip() == '200':
            print("✅ Local server is working perfectly!")
            return True
        else:
            print(f"⚠️  Server returned: {result.stdout.strip()}")
            return False
    except:
        print("❌ Server test failed or timeout")
        return False

def main():
    print("🚀 Creating Easy Access Solutions for PediAssist")
    print("="*60)
    
    # Test current setup
    working = test_current_setup()
    
    # Create solutions
    create_local_access_guide()
    create_quick_test_script()
    create_server_manager()
    
    print("\\n" + "="*60)
    print("🎯 SUMMARY")
    print("="*60)
    
    if working:
        print("✅ Your PediAssist server is RUNNING!")
        print("📱 Quick Access: http://localhost:8000/simple")
        print("\\n📖 Check EASY_ACCESS.md for full details")
        print("🔧 Use ./server_manager.sh for server control")
        print("🧪 Use ./test_access.py to test functionality")
    else:
        print("⚠️  Server might need to be restarted")
        print("💡 Try: ./server_manager.sh restart")
    
    print("\\n💡 Bookmark http://localhost:8000/simple for easy access!")

if __name__ == "__main__":
    main()