#!/bin/bash
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
